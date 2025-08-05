import os
import sqlite3
import pandas as pd
from datetime              import datetime
from turbovault4dbt.backend.procs.sqlite3 import generate_selected_entities, sources, generate_erd
from turbovault4dbt.backend.procs.sqlite3 import properties

class Excel:
    def __init__(self, **kwargs):
        self.todo = []
        self.config = kwargs.get('turboVaultconfigs')
        self.excel_path = self.config.get('excel_path')
        output_dir = self.config.get('output_dir')
        root = os.path.dirname(os.path.abspath(__file__))
        root = os.path.dirname(root)  ## get one step back from the root folder
        self.model_path = self.config.get('model_path')
        if output_dir:
            self.model_path = output_dir
        else:
            self.model_path = os.path.join(root, self.model_path.replace('../', ''))
        self.data_structure ={
            'print2FeedbackConsole': kwargs.get('print2FeedbackConsole'),
            'console_outputs': True,
            'cursor': None,
            'source': None,
            'generated_timestamp': datetime.now().strftime("%Y%m%d%H%M%S"),
            'rdv_default_schema': self.config.get("rdv_schema"),
            'model_path': self.model_path,
            'hashdiff_naming': self.config.get('hashdiff_naming'),
            'stage_default_schema': self.config.get("stage_schema"),  
            'source_list': None  ,
            'generateSources': False,
            'source_name' : None, # "Source" field splits into this field
            'source_object' : None, # "Source" field splits into this field
            }  

    
    def setTODO(self, **kwargs):
        self.SourceYML = kwargs.pop('SourceYML')
        self.todo = kwargs.pop('Tasks')
        self.DBDocs = kwargs.pop('DBDocs')
        self.Properties = kwargs.pop('Properties')
        self.selectedSources = kwargs.pop('Sources')
        
    def __initializeInMemoryDatabase(self):
        db = sqlite3.connect(':memory:')
        dfs = pd.read_excel(self.excel_path, sheet_name=None)
        for table, df in dfs.items():
            df.to_sql(table, db)

        return db.cursor()  
                     
    def read(self):
        self.data_structure['cursor'] = self.__initializeInMemoryDatabase()
        self.data_structure['cursor'].execute("SELECT DISTINCT SOURCE_SYSTEM || '_' || SOURCE_OBJECT FROM source_data")
        results = self.data_structure['cursor'].fetchall()
        source_list = []
        for row in results:
            source_list.append(row[0])
        self.data_structure['source_list'] = source_list
        self.catchDatabase()
        
    def catchDatabase(self):
        if os.path.exists('dump.db'):
            os.remove('dump.db')
        self.data_structure['cursor'].execute("vacuum main into 'dump.db'")
        self.data_structure['cursor'].close()  
                   
    def reloadDatabase(self):
        db = sqlite3.connect('dump.db')
        dest = sqlite3.connect(':memory:')
        db.backup(dest)
        db.close()
        os.remove('dump.db')
        return dest.cursor()
                                     
    def run(self):
        self.data_structure['cursor'] = self.reloadDatabase()
        if self.SourceYML:
            sources.gen_sources(self.data_structure)
        try:
            for self.data_structure['source'] in self.selectedSources:
                node = self.data_structure['source']
                # Dynamically look up source_name from source_data
                cursor = self.data_structure['cursor']
                query = f"SELECT SOURCE_SYSTEM FROM source_data WHERE SOURCE_OBJECT = '{node}' LIMIT 1"
                cursor.execute(query)
                result = cursor.fetchone()
                if result:
                    self.data_structure['source_name'] = result[0]
                else:
                    self.data_structure['print2FeedbackConsole'](f"Warning: SOURCE_SYSTEM not found for node '{node}'. Skipping.")
                    continue
                self.data_structure['source_object'] = node
                generate_selected_entities.generate_selected_entities(self.todo, self.data_structure)
                if self.Properties:
                    properties.gen_properties(self.data_structure)
            self.data_structure['print2FeedbackConsole'](message= 'Process successfully executed and models are ready to be used in Datavault 4dbt.')
        except Exception as e:
            self.data_structure['print2FeedbackConsole'](message= 'No sources selected!')

        if self.DBDocs:
            generate_erd.generate_erd(self.data_structure['cursor'], self.selectedSources,self.data_structure['generated_timestamp'],self.data_structure['model_path'],self.data_structure['hashdiff_naming'])
        self.data_structure['cursor'].close()  