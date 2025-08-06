import inspect
from typing import Callable
import ast
import time
import traceback
from numbers import Number
from datetime import date, datetime
from uuid import uuid4
from .page_layout import ApplicationPage
from .application_building_utils import SHEET_CACHE, ACCEPTABLE_AGGREGATIONS, IMPORTS, init_sheet, load_sheet, \
    get_column, info, \
    error, feedback, load_dashboard, PALETTES, init_logs


class ApplicationBuilder:

    def __init__(self,
                 kawa_client,
                 name,
                 sidebar_color=None,
                 palette=None,
                 palette_name=None,
                 create_default_components=True):
        self._k = kawa_client
        self._name = name
        self._datasets = []
        self._pages = []
        self._text_filters = {}
        self._model = None
        self._application_id = None
        self._application_url = None
        self._agent = None
        self._sidebar_color = sidebar_color
        self._create_default_components = create_default_components

        init_logs()

        if palette_name:
            self._palette = PALETTES.get(palette_name)
        else:
            self._palette = palette

    def create_model(self, dataset):
        self._model = DataModel(
            kawa=self._k,
            name=self._name,
            dataset=dataset,
            application=self,
        )
        return self._model

    def application_id(self):
        return self._application_id

    def agent_id(self):
        if self._agent:
            return self._agent.agent_id()

    def data_is_configured(self):
        return bool(self._model)

    def create_dataset(self, name: str, generator: Callable):
        existing_names = [d.name() for d in self._datasets]
        if name in existing_names:
            raise Exception(f'A dataset with the name {name} already exists. Please pick a different one')

        dataset = DataSet(
            kawa=self._k,
            name=name,
            generator=generator,
        )
        self._datasets.append(dataset)
        return dataset

    def create_page(self, name: str):
        existing_names = [d.name() for d in self._pages]
        if name in existing_names:
            raise Exception(f'A page with the name {name} already exists. Please pick a different one')

        page = ApplicationPage(
            kawa_client=self._k,
            data_model=self._model,
            name=name,
        )
        self._pages.append(page)
        return page

    def create_text_filter(self, name, filtered_column=None, source=None, value_loader=None):
        # Merges filters with the same name
        if name not in self._text_filters:
            self._text_filters[name] = TextFilter(kawa=self._k, name=name)

        self._text_filters[name].append_column(
            sheet_id_supplier=lambda: source.sheet_id() if source else self._model.sheet_id(),
            # If filtered column is not specified, rever to name
            column_name=filtered_column or name,
        )

    def create_ai_agent(self, name, instructions, color=None):
        self._agent = Agent(
            kawa=self._k,
            name=name,
            instructions=instructions,
            color=color,
        )

    def publish(self):

        info('---' * 30)
        info(f'🚀 Publishing app "{self._name}" to {self._k.kawa_api_url}')
        info('---' * 30)
        try:
            self.sync()
            self._health_check()
        # except Exception as e:
        #     traceback.print_stack()
        #     error(f'Global error while publishing: {e}')
        finally:
            if self.data_is_configured():
                feedback(self.url())

    def url(self):
        return self._application_url

    def sync(self):

        if self._agent:
            self._agent.sync()

        if not self._model and not self._datasets:
            info('👻 No data configured')
            return

        for dataset in self._datasets:
            dataset.sync()

        if not self._model:
            # By default, init the model on the first dataset
            self.create_model(self._datasets[0])

        self._model.sync()

        if not self._model.sheet_id():
            raise Exception('The underlying model has not been synced')

        self._init_application()

        for page in self._pages:
            page.sync(application_id=self._application_id)

        SHEET_CACHE.clear()
        for text_filter in self._text_filters.values():
            text_filter.sync(application_id=self._application_id)

    def _health_check(self, iteration=1):

        if not self.data_is_configured():
            return

        max_iter = 10
        if iteration > max_iter:
            error(f'🚨 Application is not healthy after allocated wait time')

        num_datasets = len(self._datasets)
        failures = []

        if iteration == 1:
            ds = 'datasets' if num_datasets > 1 else 'dataset'
            info(f'🚑 Running healthcheck on {num_datasets} {ds}')
            for dataset in self._datasets:
                info(f'--> {dataset.name()}')

            time.sleep(5)
        else:
            info(f'🚑 Retry {iteration - 1}/{max_iter}')
            time.sleep(iteration)

        for dataset in self._datasets:
            ds_id = str(dataset.datasource_id())
            url = f'{self._k.kawa_api_url}/backoffice/datasources/health-report/v2/{ds_id}'
            health_reports = self._k.get(url)
            chronological = sorted(health_reports, key=lambda x: x['synchronizationState']['startTime'])
            last_report = chronological[-1]
            status = last_report['synchronizationState']['status']

            if status == 'SUCCESS':
                info(f'💚 Dataset {dataset.name()} is healthy')
            elif status == 'RUNNING':
                info(f'🕣 Dataset {dataset.name()} is still running - let\'s wait a bit and check again.')
                self._health_check(iteration + 1)
            elif status == 'FAILURE':
                error(f'🚨 Dataset {dataset.name()} is NOT healthy')
                error(last_report['synchronizationState']['logAnswer']['log'])
                failures.append(dataset.name())

        if failures:
            error(f'🚨 Application is not healthy')

    def _init_application(self):
        if self._palette and len(self._palette) > 7:
            self._k.commands.run_command('replaceWorkspacePalette', {
                "workspaceId": self._k.active_workspace_id,
                "palette": {
                    "colors": self._palette,
                    "enabled": True
                }
            })

        existing_applications = self._k.entities.applications().list_entities_by_name(self._name)
        if existing_applications:
            application_id = str(existing_applications[0]['id'])
            self._k.commands.run_command('deleteApplication', {'applicationId': application_id})

        created_app = self._k.commands.run_command('createApplication', {
            "displayInformation": {
                "displayName": self._name,
                "description": ""
            },
            "sheetIds": [d.sheet_id() for d in self._datasets],
            "agentIds": [self.agent_id()] if self.agent_id() else [],
            "createDefaultComponents": self._create_default_components,
        })['application']

        workspace_id = created_app['workspaceId']
        base_url = self._k.kawa_api_url
        self._application_id = created_app['id']
        self._application_url = f'{base_url}/workspaces/{workspace_id}/applications/{self._application_id}'
        info(f'⚙️ Application {self._name} was created (id={self._application_id})')

        if self._sidebar_color:
            self._k.commands.run_command('replaceApplicationDisplayParameters', {
                "applicationId": str(self._application_id),
                "displayParameters": {
                    "color": self._sidebar_color,
                }
            })

        return self._application_id


class DataModel:

    def __init__(self, kawa, name, application, dataset):
        self._dataset = dataset
        self._name = name
        self._k = kawa
        self._sheet_id = None
        self._application = application
        self._relationships = []
        self._metrics = []
        self._variables = []

    def sync(self):
        info('⚙️ Creating the model')
        primary_datasource_id = self._dataset.datasource_id()
        if primary_datasource_id is None:
            raise Exception('The underlying dataset has not been synced')

        for rel in self._relationships:
            rel.sync()

        for var in self._variables:
            var.sync()

        for metric in self._metrics:
            metric.sync(sheet_id=self.sheet_id())

    def sheet_id(self):
        return self._dataset.sheet_id()

    def application_id(self):
        return self._application.application_id()

    def create_variable(self, name, kawa_type, initial_value):
        variable = Variable(
            kawa=self._k,
            sheet_id_supplier=lambda: self.sheet_id(),
            name=name,
            kawa_type=kawa_type,
            initial_value=initial_value
        )
        self._variables.append(variable)

    def create_relationship(self, name, dataset, link):
        rel = Relationship(
            kawa=self._k,
            model=self,
            name=name,
            dataset=dataset,
            link=link,
        )
        self._relationships.append(rel)
        return rel

    def create_metric(self, name, formula=None, prompt=None):

        sql = None
        if formula:
            normalized = formula.strip().upper()
            if not normalized.startswith("SELECT"):
                sql = f"SELECT {formula}"
            else:
                sql = formula

        self._metrics.append(
            Metric(
                kawa=self._k,
                name=name,
                sql=sql,
                prompt=prompt,
            )
        )


class Relationship:

    def __init__(self, kawa, name, model, dataset, link):
        self._k = kawa
        self._name = name
        self._dataset = dataset
        self._model = model
        self._link = link
        self._cached_sheet = None
        self._columns = []

    def add_column(self, name, aggregation, new_column_name):
        uc_aggregation = aggregation.upper()
        if uc_aggregation not in ACCEPTABLE_AGGREGATIONS:
            raise Exception('The aggregation is not known, please use one of: ' + ','.join(ACCEPTABLE_AGGREGATIONS))

        self._columns.append({
            'name': name,
            'aggregation': uc_aggregation,
            'new_column_name': new_column_name,
        })

    def sync(self):
        info(f'🔗 Creating relationship {self._name}')
        if not self._columns:
            # No columns added in this relationship, nothing to do
            return

        datasource_id = self._dataset.datasource_id()
        if not datasource_id:
            raise Exception('The underlying dataset has not been synced')

        if not self._link:
            raise Exception('There is no definition for the link in this relationship')

        source_sheet = load_sheet(kawa=self._k, sheet_id=self._model.sheet_id())
        target_sheet = load_sheet(kawa=self._k, sheet_id=self._dataset.sheet_id())

        joins = []
        for source, target in self._link.items():
            source_column = get_column(source_sheet, source)
            target_column = get_column(target_sheet, target)
            joins.append({
                "targetColumnId": target_column['columnId'],
                "sourceColumnId": source_column['columnId'],
            })

        for column in self._columns:
            lookup_column = get_column(target_sheet, column['name'])

            updated_sheet = self._k.commands.run_command(
                command_name='addLookupField',
                command_parameters={
                    # This is the source layout
                    "layoutId": str(source_sheet['defaultLayoutId']),
                    # This is the target sheet
                    "linkedSheetId": str(target_sheet['id']),
                    "columnDefinitions": [
                        {
                            # This is the column to bring from the target sheet
                            "columnId": lookup_column['columnId'],
                            "aggregation": column['aggregation']
                        }
                    ],
                    "joins": joins
                }
            )

            new_column = [c for c in updated_sheet['sheetColumns']
                          if c['displayInformation']['displayName'].startswith(column['name'] + ' by')][0]

            self._k.commands.run_command(
                command_name='replaceColumnDisplayInformation',
                command_parameters={
                    "sheetDataModelModifier": {
                        "columnId": new_column['columnId'],
                        "sheetId": source_sheet['id'],
                    },
                    "displayInformation": {
                        "displayName": column['new_column_name'],
                        "description": ""
                    }
                }
            )


class DataSet:

    def __init__(self, kawa, name: str, generator: Callable):
        self._k = kawa
        self._name = name
        self._generator = generator
        self._datasource_id = None
        self._sheet_id = None

    def name(self):
        return self._name

    def datasource_id(self):
        return self._datasource_id

    def sheet_id(self):
        return self._sheet_id

    def sync(self):
        start = time.time()
        info(f'📚 Sync dataset: {self._name}')
        function_code = inspect.getsource(self._generator)
        imports = '\n'.join(IMPORTS)
        source_code = f'{imports}\n\n{function_code}'

        indicator_types = self._extract_outputs(source_code)
        script_id = self._init_script(source_code)

        self._init_datasource(
            indicator_types=indicator_types,
            script_id=script_id,
        )

        self._init_sheet()

        end = time.time()
        info(f'📚 The {self._name} dataset has been synced in {end - start:.1f}s')

    def _init_script(self, source_code):
        existing_scripts = self._k.entities.scripts().list_entities_by_name(self._name)
        if existing_scripts:
            script_id = str(existing_scripts[0]['id'])
            self._k.commands.run_command('deleteScript', {'scriptId': script_id})

        created_script_id = self._k.commands.run_command(
            command_name='createScript',
            command_parameters={'name': self._name, 'content': source_code}
        )['id']

        info(f'⚙️ Script {self._name} was created (id={created_script_id})')
        return created_script_id

    def _init_datasource(self, indicator_types, script_id):

        indicators = []
        if not indicator_types:
            raise Exception('No indicators were found in the the underlying script')
        else:
            for indicator_id, indicator_type in indicator_types.items():
                indicators.append(
                    {
                        "elementDataModel": None,
                        "displayInformation": {
                            "displayName": indicator_id,
                            "description": ""
                        },
                        "possibleValues": [],
                        "indicatorId": indicator_id,
                        "indicatorKind": "TABLE",
                        "indicatorStatus": "ACTIVE",
                        "includedInDefaultLayout": True,
                        "type": indicator_type
                    }
                )

        existing_datasources = self._k.entities.datasources().list_entities_by_name(self._name)
        if existing_datasources:
            datasource_id = str(existing_datasources[0]['id'])
            self._k.commands.run_command('archiveDataSourceAndDeleteAssociatedData', {'dataSourceId': datasource_id})

        created_datasource_id = self._k.commands.run_command(
            command_name='createEtlAndDatasource',
            command_parameters={
                "doNotCreateSheet": True,
                "isMapping": False,
                "displayInformation": {
                    "displayName": self._name,
                    "description": ""
                },
                "loadingAdapterName": 'CLICKHOUSE',
                "loadingMode": "RESET_BEFORE_INSERT",
                "extractionAdapterName": "PYTHON_SCRIPT",
                "extractionAdapterConfiguration": {
                    "scriptId": str(script_id),
                    "scriptParametersValues": []
                },
                "indicators": indicators,
                "jobTrigger": {
                    "enabled": False,
                    "scheduleType": "INTERVAL",
                    "onlyOnBusinessDays": None,
                    "interval": 3,
                    "timeUnit": "HOURS",
                    "timeZone": None,
                    "initialDelay": 0
                },
                "rowMapperConfigList": [],
                "defaultGlobalPolicy": "ALLOW_ALL",
                "createAssociatedTimeSeriesDataSource": False,
                "needsQueryCostCheck": False
            }
        )['dataSource']['id']

        info(f'⚙️ Datasource {self._name} was created (id={created_datasource_id})')
        self._datasource_id = created_datasource_id

    def _init_sheet(self):
        info(f'🗒️ Creating a sheet on top of dataset {self._name}')
        self._sheet_id = init_sheet(
            kawa=self._k,
            sheet_name=self._name,
            primary_datasource_id=self._datasource_id,
        )
        return self._sheet_id

    @staticmethod
    def _extract_outputs(source_code):
        tree = ast.parse(source_code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for deco in node.decorator_list:
                    if isinstance(deco, ast.Call) and getattr(deco.func, 'id', '') == 'kawa_tool':
                        for keyword in deco.keywords:
                            if keyword.arg == 'outputs':
                                outputs_node = keyword.value
                                outputs_src = ast.unparse(outputs_node)
                                safe_globals = {
                                    'str': 'text',
                                    'float': 'decimal',
                                    'date': 'date',
                                    'datetime': 'date_time',
                                    'bool': 'boolean',
                                }
                                return eval(outputs_src, safe_globals, {})

        return None


class Metric:

    def __init__(self, kawa, name, sql, prompt):
        if (prompt is None) == (sql is None):
            raise Exception('Define one (And only one): query or prompt')

        self._k = kawa
        self._name = name
        self._sql = sql
        self._prompt = prompt

    def sync(self, sheet_id):

        if self._prompt:
            info(f'🤖 Generate a formula for the prompt: {self._prompt}')
            generated_xml = self._k.post(
                url=f'{self._k.kawa_api_url}/gen-ai/generate-xml-formula',
                data={
                    'prompt': self._prompt,
                    'sheetId': str(sheet_id),
                }
            )['generatedXml']
            data = {'xmlSyntacticTree': generated_xml}

        else:
            info(f'📏 Sync a metric: {self._name} with sql: {self._sql}')
            data = {'sql': self._sql}

        self._k.commands.run_command('addComputedColumnToSheet', {
            'sheetId': sheet_id,
            'displayInformation': {
                'displayName': self._name,
                'description': ''
            },
            'addInDefaultLayout': True,
            **data,
        })


class Variable:

    def __init__(self, kawa, sheet_id_supplier, name, kawa_type, initial_value):
        self._k = kawa
        self._name = name
        self._type = kawa_type.lower()
        self._initial_value = initial_value
        self._sheet_id_supplier = sheet_id_supplier

    def sync(self):
        info(f'#️⃣ Registering a new variable: {self._name} or type {self._type}')
        self._k.commands.run_command('createParameterControlWithLinkedParameter', {
            "sheetId": self._sheet_id_supplier(),
            "parameterConfiguration": {
                "type": self._type,
                "initialValue": self._formatted_initial_value(),
            },
            "controlConfiguration": {
                "displayInformation": {
                    "displayName": self._name,
                    "description": ""
                },
                "controlParameters": {
                    "control": self._control_type(),
                    "size": "md"
                }
            }
        })

    def _formatted_initial_value(self):
        init = self._initial_value
        if self._type == 'text':
            return str(init) if init else ''
        elif self._type == 'decimal' or self._type == 'integer':
            return init if isinstance(init, Number) else 0
        elif self._type == 'date':
            return (init - date(1790, 1, 1)).days if isinstance(init, date) else None
        elif self._type == 'date_time':
            return int(init.timestamp() * 1000) if isinstance(init, datetime) else None
        elif self._type == 'boolean':
            return bool(init)
        else:
            raise Exception(f'Unsupported type for control {self._name}: {self._type}')

    def _control_type(self):
        if self._type == 'text':
            return 'TEXT_INPUT'
        elif self._type == 'decimal' or self._type == 'integer':
            return 'NUMBER_INPUT'
        elif self._type == 'boolean':
            return 'TOGGLE'
        elif self._type == 'date':
            return 'DATE_INPUT'
        elif self._type == 'date_time':
            return 'DATETIME_INPUT'
        else:
            raise Exception(f'Unsupported type for control {self._name}: {self._type}')


class TextFilter:

    def __init__(self, kawa, name):
        self._k = kawa
        self._name = name
        self._columns = []

    def append_column(self, sheet_id_supplier, column_name):
        self._columns.append({
            'sheet_id_supplier': sheet_id_supplier,
            'name': column_name
        })

    def sync(self, application_id):
        info(f'⚙️ Sync filter {self._name}')

        apply_to = []
        for column in self._columns:
            sheet_id_supplier = column['sheet_id_supplier']
            column_name = column['name']

            sheet_id = sheet_id_supplier()
            sheet = load_sheet(self._k, sheet_id)
            column = get_column(sheet, column_name)

            apply_to.append({
                'columnId': column['columnId'],
                'sheetId': str(sheet_id),
            })

        self._k.commands.run_command('createFilterControlWithLinkedFilter', {
            "applicationId": str(application_id),
            "filterConfiguration": {
                "filterType": "TEXT_FILTER",
                "applyTo": apply_to,
                "filterOutNullValues": True
            },
            "controlConfiguration": {
                "displayInformation": {
                    "displayName": self._name,
                    "description": ""
                },
                "controlParameters": {
                    "mode": "ValuesList",
                    "multiSelection": True,
                    "size": "md"
                }
            }
        })

        ...
        # sheet_id = sheet_id_supplier()
        # sheet = load_sheet(self._k, sheet_id)
        # column = get_column(sheet, column_name)
        # self._targets.append(column)


class Agent:

    def __init__(self, kawa, name, instructions='', color=None):
        self._k = kawa
        self._name = name
        self._color = color or "#ec1254"
        self._agent_id = None
        self._instructions = instructions or ''

    def agent_id(self):
        return self._agent_id

    def sync(self):
        info(f'🤖 Sync an AI agent: {self._name}')
        existing_agents = self._k.entities.agents().list_entities_by_name(self._name)
        if existing_agents:
            agent_id = str(existing_agents[0]['id'])
            self._k.commands.run_command('deleteAgent', {'agentId': agent_id})

        created_agent_id = self._k.commands.run_command('createAgent', {
            "displayInformation": {
                "displayName": self._name,
                "extraInformation": {
                    "color": self._color,
                }
            },
            "instructions": [self._instructions],
            "commands": [],
            "knowledgeIds": [],
            "capabilities": {
                "sendEmails": False,
                "internetSearch": False,
                "querySheet": True,
                "useAttachedFiles": True
            }
        })['id']

        self._agent_id = created_agent_id
