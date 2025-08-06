#!/usr/bin/env python
# coding: utf-8

# ## functions prod final 29_07
# 
# New notebook

# In[1]:


from datetime import datetime
from notebookutils import mssparkutils
import pytz
from sempy.fabric.exceptions._exceptions import FabricHTTPException
from pyspark.sql.types import StructType, StructField, StringType, IntegerType,TimestampType
from pyspark.sql import functions as F
from pyspark.sql.functions import concat,col,concat_ws, trim, lower, lit, when, udf, expr,regexp_replace
import sempy.fabric as fabric 
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from itertools import chain
import json
import re
from pyspark.sql.types import *
from pyspark.sql import SparkSession
from functools import reduce
from delta.tables import *
from pyspark.sql.functions import regexp_extract
import pandas as pd
from collections import defaultdict, deque
from pyspark.sql.types import StructType, StructField, StringType
from collections import defaultdict, deque


# In[20]:


spark = SparkSession.builder \
    .appName("oct") \
    .getOrCreate()

spark.conf.set("spark.sql.legacy.parquet.datetimeRebaseModeInWrite", "LEGACY")


def get_executer_alias():
    try:
        executing_user = mssparkutils.env.getUserName()
        at_pos = executing_user.find('@')
        executing_user = executing_user[:at_pos]
    except Exception as e:
        msg = str(e)
        msg = msg.replace('"',"'")
        executing_user = msg = msg.replace("'",'"')
    return executing_user


# In[21]:


def get_modifiedtimestamp():
    try:
        pst_timezone = pytz.timezone('US/Pacific')
        current_time_utc = datetime.now(pytz.utc)
        current_time_pst = current_time_utc.astimezone(pst_timezone)
        current_time_pst = current_time_pst.replace(microsecond=0)
        current_time_pst = current_time_pst.replace(tzinfo=None)
    except Exception as e:
        current_time_pst = datetime(1900, 1, 1, 0, 0, 0)
    return current_time_pst


# In[22]:


def convert_to_pst(date_str):
    try:
        utc_time = datetime.fromisoformat(date_str)
        pst = pytz.timezone('US/Pacific')
        pst_time = utc_time.astimezone(pst)
        pst_time = pst_time.replace(microsecond=0)
        pst_time = pst_time.replace(tzinfo=None)
    except Exception as e:
        pst_time = datetime(1900, 1, 1, 0, 0, 0)
    return pst_time


# In[23]:


def get_workspace_name(WorkspaceID):
    alias = get_executer_alias()
    modified_time = get_modifiedtimestamp()
    try:
        WorkspaceID = WorkspaceID.lower()
        client = fabric.FabricRestClient()
        url = f'https://api.fabric.microsoft.com/v1/workspaces/{WorkspaceID}/'
        response = client.get(url)
        metadata = response.json()

        WorkspaceName = metadata.get('displayName','Unknown')
        message = f"{WorkspaceName} workspace name retrieval is successfull "

    except FabricHTTPException as e:
        error_response = e.response.json()
        error_code = error_response.get("errorCode", "UnknownError")
        error_msg = error_response.get("message", "No message found")
        message = f"{error_code} - {error_msg}"
        message = message.replace('"', "'").replace("'", '"')
        WorkspaceName = "Unknown"
    except Exception as e:
        message = str(e)
        message = message.replace('"', "'").replace("'", '"')
        WorkspaceName = "Unknown"
    schema = StructType([
    StructField("ID", StringType(), True),
    StructField("Name", StringType(), True),
    StructField("Info", StringType(), True),
    StructField("Alias", StringType(), True),
    StructField("ModifiedTime", TimestampType(), True)
    ])
    spark_df = spark.createDataFrame([(WorkspaceID,WorkspaceName,message,alias,modified_time)], schema)
    return spark_df


# In[24]:


def get_dataset_name(WorkspaceID, DatasetID):
    alias = get_executer_alias()
    modified_time = get_modifiedtimestamp()
    try:
        WorkspaceID = WorkspaceID.lower()
        DatasetID = DatasetID.lower()
        client = fabric.FabricRestClient()
        url = f'https://api.fabric.microsoft.com/v1/workspaces/{WorkspaceID}/items/{DatasetID}'
        response = client.get(url)
        metadata = response.json()
        dataset_name = metadata.get("displayName", "Unknown")
        message = f"{dataset_name} dataset name is retrieved"
    except FabricHTTPException as e:
        error_response = e.response.json()
        error_code = error_response.get("errorCode", "UnknownError")
        error_msg = error_response.get("message", "No message found")
        message = f"{error_code} - {error_msg}"
        dataset_name = "Unknown"
        message = message.replace('"', "'").replace("'", '"')
    except Exception:
        message = str(e)
        dataset_name = "Unknown"
        message = message.replace('"', "'").replace("'", '"')
    
    schema = StructType([
    StructField("WorkspaceID", StringType(), True),
    StructField("ID", StringType(), True),
    StructField("Name", StringType(), True),
    StructField("Info", StringType(), True),
    StructField("Alias", StringType(), True),
    StructField("ModifiedTime", TimestampType(), True)
    ])
    spark_df = spark.createDataFrame([(WorkspaceID,DatasetID,dataset_name,message,alias,modified_time)], schema)
    return spark_df


# In[25]:


def get_lakehouse_name(WorkspaceID,LakehouseID):
    alias = get_executer_alias()
    modified_time = get_modifiedtimestamp()

    try:
        WorkspaceID = WorkspaceID.lower()
        LakehouseID = LakehouseID.lower()
        client = fabric.FabricRestClient()
        url = f'https://api.fabric.microsoft.com/v1/workspaces/{WorkspaceID}/items/{LakehouseID}'
        response = client.get(url)
        metadata = response.json()
        LakehouseName = metadata.get("displayName", "Unknown")
        message = f"{LakehouseName} dataset name is retrieved"
    except FabricHTTPException as e:
        LakehouseName = "Unknown"
        error_response = e.response.json()
        error_code = error_response.get("errorCode", "UnknownError")
        error_msg = error_response.get("message", "No message found")
        message = f"{error_code} - {error_msg}"
    except Exception:
        LakehouseName = "Unknown"
        message = str(e)
        message = message.replace('"', "'").replace("'", '"')

    schema = StructType([
    StructField("WorkspaceID", StringType(), True),
    StructField("ID", StringType(), True),
    StructField("Name", StringType(), True),
    StructField("Info", StringType(), True),
    StructField("Alias", StringType(), True),
    StructField("ModifiedTime", TimestampType(), True)
    ])
    spark_df = spark.createDataFrame([(WorkspaceID,LakehouseID,LakehouseName,message,alias,modified_time)], schema)
    return spark_df


# In[26]:


def parameters_check(oct_param_table,function_name,workspaceid,id = "NA"): 
    message = "Operation Completed"
    df_table = spark.sql(f"select count(1) as output from {oct_param_table} where ID = '{id}' and Name != 'Unknown'")
    df_table = df_table.filter(F.col("output") == 0).count()
    if df_table == 1:
        if function_name == "get_workspace_name":
            get_workspace_name(WorkspaceID=workspaceid)
        elif function_name == "get_dataset_name":
            get_dataset_name(WorkspaceID= workspaceid, DatasetID=id)
        elif function_name == "get_lakehouse_name":
            get_lakehouse_name(WorkspaceID=workspaceid,LakehouseID=id)
        else: 
            message = "parameter check failed"
    return message


# In[27]:


def insert_update_stage_oct(spark_df, oct_table_name, on_name, errors_flag="No",error_type = "NA"):
    if errors_flag == "No":
        distinct_values = tuple(row[on_name] for row in spark_df.select(on_name).distinct().collect())
        if len(distinct_values) == 1:
            spark.sql(f"DELETE FROM {oct_table_name} WHERE {on_name} = '{distinct_values[0]}'")
        elif len(distinct_values) == 0:
            pass
        else:
            spark.sql(f"DELETE FROM {oct_table_name} WHERE {on_name} IN {distinct_values}")
        spark_df.write.format("delta").mode("append").saveAsTable(oct_table_name)
    else:
        distinct_values = tuple(row[on_name] for row in spark_df.select(on_name).distinct().collect())
        if len(distinct_values) == 1:
            spark.sql(f"DELETE FROM {oct_table_name} WHERE {on_name} = '{distinct_values[0]}' and Item_type = '{error_type}'")
        elif len(distinct_values) == 0:
            pass
        else:
            spark.sql(f"DELETE FROM {oct_table_name} WHERE {on_name} IN {distinct_values} and Item_type = '{error_type}'")
        spark_df.write.format("delta").mode("append").saveAsTable(oct_table_name)
    return "Merge Operation Completed"


# In[28]:


def get_shortcuts(WorkspaceID,LakehouseID):
    try:
        Alias = get_executer_alias()
        ModifiedTime = get_modifiedtimestamp()
        client = fabric.FabricRestClient()
        response = client.get(f"https://api.fabric.microsoft.com/v1/workspaces/{WorkspaceID}/items/{LakehouseID}/shortcuts")
        json_data = response.json().get("value", [])
        for json_value in json_data:
                json_value["initial_workspace_id"] = WorkspaceID
                json_value["initial_lakehouse_id"] = LakehouseID
                json_value["Alias"] = Alias
                json_value["ModifiedTime"] = ModifiedTime
    except FabricHTTPException as e:
        LakehouseName = "Unknown"
        error_response = e.response.json()
        error_code = error_response.get("errorCode", "UnknownError")
        error_msg = error_response.get("message", "No message found")
        message = f"{error_code} - {error_msg}"
        json_data = [{"WorkspaceID": WorkspaceID, "Type": "Shortcuts", "LakehouseID": LakehouseID, "Message": str(message), "Alias": Alias, "ModifiedTime": ModifiedTime}]
    except Exception as e:
        message = str(e)
        json_data = [{"WorkspaceID": WorkspaceID, "Type": "Shortcuts", "LakehouseID": LakehouseID, "Message": str(message), "Alias": Alias, "ModifiedTime": ModifiedTime}]
    return json_data


# In[29]:


def parallelize_api_call(lakehouse_df):  
    rows = lakehouse_df.select("WorkspaceID", "ID").rdd.map(lambda row: (row["WorkspaceID"], row["ID"])).collect()
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_input = {executor.submit(get_shortcuts, WorkspaceID, ID): (WorkspaceID, ID) for WorkspaceID, ID in rows}
        for future in as_completed(future_to_input):
            try:
                result = future.result()  
                results.append(result)
            except Exception as e:
                print(f"Error processing 1 {future_to_input[future]}: {e}")     
    return list(chain.from_iterable(results))  


# In[30]:


def nested_parallelize(lakehouse_df,final_results =[]):
    schema = StructType([
                    StructField("workspaceId", StringType(), True),
                    StructField("itemId", StringType(), True),
                    ])
    results = parallelize_api_call(lakehouse_df)
    data = [
        {
            "itemId": r.get("target", {"oneLake": {}}).get("oneLake", {}).get("itemId", "NA"),
            "workspaceId": r.get("target", {"oneLake": {}}).get("oneLake", {}).get("workspaceId", "NA"),
        }
    for r in results if isinstance(r, dict)
    ]
    lakehouse_df = spark.createDataFrame(data,schema)
    lakehouse_df = lakehouse_df.select(col("workspaceId").alias("WorkspaceID"), col("itemId").alias('ID'))
    lakehouse_df = lakehouse_df.filter(lakehouse_df["ID"] != "NA")
    if not(lakehouse_df.isEmpty()):
        lakehouse_df = lakehouse_df.drop_duplicates()
    final_results = final_results + results
    if lakehouse_df.isEmpty():
        pass
    else:
        results = parallelize_api_call(lakehouse_df)
        data = [
            {
                "itemId": r.get("target", {"oneLake": {}}).get("oneLake", {}).get("itemId", "NA"),
                "workspaceId": r.get("target", {"oneLake": {}}).get("oneLake", {}).get("workspaceId", "NA"),
            }
        for r in results if isinstance(r, dict)
        ]
        lakehouse_df = spark.createDataFrame(data,schema)
        lakehouse_df = lakehouse_df.select(col("workspaceId").alias("WorkspaceID"), col("itemId").alias('ID')).dropDuplicates()
        lakehouse_df = lakehouse_df.filter(lakehouse_df["ID"] != "NA")
        final_results = final_results + results
        if not(lakehouse_df.isEmpty()):
            lakehouse_df = lakehouse_df.drop_duplicates()
    return final_results


# In[31]:


def build_path(node_id, parent_map):
    path = []
    while node_id is not None:
        path.insert(0, node_id)
        node_id = parent_map.get(node_id)
    return ">".join(path)


# In[32]:


def process_shortcuts():
    df = spark.sql("""SELECT Initial_Path,
                            CASE
                            WHEN source_path LIKE '%https://msit-onelake.dfs.fabric.microsoft.com/nan/nan/nan%' THEN NULL
                            ELSE source_path
                            END AS SourcePath
                    FROM oct_shortcuts_stage""")
    parent_map = dict(df.rdd.map(lambda row: (row["Initial_Path"], row["SourcePath"])).collect())

    # Perform recursive resolution in Python
    path_data = [(key, build_path(key, parent_map)) for key in parent_map.keys()]
    schema = StructType([
                    StructField("Initial_Path", StringType(), True),
                    StructField("path", StringType(), True),
                    ])

    path_df = spark.createDataFrame(path_data, schema)
    df_with_path = df.join(path_df, on="Initial_Path", how="left")

    df_final = df_with_path.withColumn(
        "Final_Source_Path",
        expr("""
            CASE WHEN INSTR(path, '>') > 0 THEN SUBSTRING(path, 0, INSTR(path, '>')-1) ELSE path END
        """)
    )
    df_final.createOrReplaceTempView("Final_Source_path_Extraction_view")

    final = spark.sql(""" 
        select distinct a.initial_workspace_id as InitialWorkspaceID,
                a.initial_lakehouse_id as InitialLakehouseID,
                l.Name as InitialLakehouseName,
                concat("https://msit.powerbi.com/groups/",a.initial_workspace_id,"/lakehouses/",a.initial_lakehouse_id,"?experience=power-bi") as InitialLakehouseLink,
                a.Initial_Path,
                CASE WHEN a.Initial_Path LIKE 'https://%' THEN CONCAT('abfss://',SPLIT(a.Initial_Path, '/')[3],'@',SPLIT(a.Initial_Path, '/')[2],'/',
                                        CONCAT_WS('/', SLICE(SPLIT(a.Initial_Path, '/'), 5, 100))) ELSE a.Initial_Path
                                    END AS Initial_abfsspath
                ,a.shortcutName as Initial_Shortcut_Name,
                split(regexp_replace(b.Final_Source_Path, '^https://msit-onelake\.dfs\.fabric\.microsoft\.com/', ''), '/')[0] AS FinalSourceWorkspaceID,
                split(regexp_replace(b.Final_Source_Path, '^https://msit-onelake\.dfs\.fabric\.microsoft\.com/', ''), '/')[1] AS FinalSourceLakehouseID,
                fl.Name as FinalSourceLakehouseName,
                concat("https://msit.powerbi.com/groups/",split(regexp_replace(b.Final_Source_Path, '^https://msit-onelake\.dfs\.fabric\.microsoft\.com/', ''), '/')[0],"/lakehouses/",split(regexp_replace(b.Final_Source_Path, '^https://msit-onelake\.dfs\.fabric\.microsoft\.com/', ''), '/')[1],"?experience=power-bi") as FinalSourceLakehouseLink,
                regexp_extract(b.Final_Source_Path, '.*/([^/]+)$', 1) as Final_Shortcut_Name,
                b.Final_Source_Path,
                CASE WHEN b.Final_Source_Path LIKE 'https://%' THEN CONCAT('abfss://',SPLIT(b.Final_Source_Path, '/')[3],'@',SPLIT(b.Final_Source_Path, '/')[2],'/',
                                        CONCAT_WS('/', SLICE(SPLIT(b.Final_Source_Path, '/'), 5, 100))) ELSE b.Final_Source_Path
                                    END AS Final_Source_abfsspath
                ,c.initial_adls_path as Source_ADLS_Path,
                case when d.Lakehouse_ID is not null then "Yes" else "No" end as OSOTLakehouseFlag,
                coalesce(d.Lakehouse_Type,'Not Authoritative') as SourceLakehouseType,
                coalesce(d.`Area/Domain`,'Not Authoritative') as Source_Area_Domain,
                a.Alias,
                a.ModifiedTime
        from oct_shortcuts_stage a 
        join Final_Source_path_Extraction_view b on a.initial_path = b.Initial_Path
        left join oct_shortcuts_stage c on b.Final_Source_Path = c.initial_path
        left join delta.`abfss://ed6737e8-6e3a-4d64-ac9c-3441eec71500@msit-onelake.dfs.fabric.microsoft.com/1df68066-3cfa-44a9-86fe-16135cd86ae8/Tables/OSOT_Lakehouses` d on lcase(trim(split(regexp_replace(b.Final_Source_Path, '^https://msit-onelake\.dfs\.fabric\.microsoft\.com/', ''), '/')[1])) = lcase(trim(d.Lakehouse_ID))
        left join lakehouselist l on lcase(trim(l.ID)) = lcase(trim(a.initial_lakehouse_id))  
        left join lakehouselist fl on lcase(trim(fl.ID))  = lcase(trim(split(regexp_replace(b.Final_Source_Path, '^https://msit-onelake\.dfs\.fabric\.microsoft\.com/', ''), '/')[1]))
    """)   
    final.write.format("delta").mode("overwrite").saveAsTable("oct_shortcuts")
    return final


# In[33]:


def final_all_list_lakehousenames():
    final_shortcut_list = spark.sql("select distinct source_workspace_id, source_lakehouse_id from oct_shortcuts_stage where source_lakehouse_id is not null and source_workspace_id is not null")
    lakehouse_schema = StructType([
            StructField("WorkspaceID", StringType(), True),
            StructField("ID", StringType(), True),
            StructField("Name", StringType(), True),
            StructField("Info", StringType(), True),
            StructField("Alias", StringType(), True),
            StructField("ModifiedTime", TimestampType(), True)
            ])
    lakehousenames = spark.createDataFrame([],lakehouse_schema)
    for row in final_shortcut_list.toLocalIterator():
        WorkspaceID = row["source_workspace_id"]
        LakehouseID = row["source_lakehouse_id"]
        Lakehousenames_stage = get_lakehouse_name(WorkspaceID,LakehouseID)
        lakehousenames = lakehousenames.unionByName(Lakehousenames_stage)
    inital_lakehouse_list = spark.sql("select ID FROM lakehouselist")
    lakehousenames = lakehousenames.join(inital_lakehouse_list, on="ID", how="left_anti")
    lakehousenames.write.format("delta").mode("append").saveAsTable("lakehouselist")
    return lakehousenames


# In[34]:


def final_list_lakehousenames():
    final_shortcut_list = spark.sql("select distinct source_workspace_id, source_lakehouse_id from oct_shortcuts_stage where source_lakehouse_id is not null and source_workspace_id is not null except select WorkspaceID, ID from lakehouselist")
    lakehouse_schema = StructType([
            StructField("WorkspaceID", StringType(), True),
            StructField("ID", StringType(), True),
            StructField("Name", StringType(), True),
            StructField("Info", StringType(), True),
            StructField("Alias", StringType(), True),
            StructField("ModifiedTime", TimestampType(), True)
            ])
    lakehousenames = spark.createDataFrame([],lakehouse_schema)
    for row in final_shortcut_list.toLocalIterator():
        WorkspaceID = row["source_workspace_id"]
        LakehouseID = row["source_lakehouse_id"]
        Lakehousenames_stage = get_lakehouse_name(WorkspaceID,LakehouseID)
        lakehousenames = lakehousenames.unionByName(Lakehousenames_stage)
    inital_lakehouse_list = spark.sql("select ID FROM lakehouselist")
    lakehousenames = lakehousenames.join(inital_lakehouse_list, on="ID", how="left_anti")
    lakehousenames.write.format("delta").mode("append").saveAsTable("lakehouselist")
    return lakehousenames


# In[35]:


def final_all_shortcuts():
    lakehouse_df = spark.sql("select WorkspaceID,ID from lakehouselist")
    final_results = nested_parallelize(lakehouse_df, final_results=[])

    shortcutsAPI_Schema = StructType([
        StructField("name", StringType(), True),
        StructField("path", StringType(), True),
        StructField("target", StructType([
            StructField("type", StringType(), True),
            StructField("oneLake", StructType([
                StructField("itemId", StringType(), True),
                StructField("path", StringType(), True),
                StructField("workspaceId", StringType(), True)
            ]), True),
            StructField("adlsGen2", StructType([
                StructField("connectionId", StringType(), True),
                StructField("location", StringType(), True),
                StructField("subpath", StringType(), True)
            ]), True)
        ]), True),
        StructField("initial_workspace_id", StringType(), True),
        StructField("initial_lakehouse_id", StringType(), True),
        StructField("Alias", StringType(), True),
        StructField("ModifiedTime", TimestampType(), True),
    ])

    shortcuts = spark.createDataFrame(final_results, shortcutsAPI_Schema).dropDuplicates()

    shortcuts = shortcuts.withColumn(
        "ShortcutName",
        concat(
            when(col("path").contains("/Tables/"),
                 concat(regexp_replace(col("path"), "/Tables/", ""), lit(".")))
            .when(col("path").contains("/Tables"),
                  concat(regexp_replace(col("path"), "/Tables", "dbo"), lit(".")))
            .otherwise(lit("")),
            col("name")
        )
    ).select(
        col("initial_workspace_id"),
        col("initial_lakehouse_id"),
        col("ShortcutName"),
        concat(
            lit("https://msit-onelake.dfs.fabric.microsoft.com/"),
            col("initial_workspace_id"),
            lit("/"),
            col("initial_lakehouse_id"),
            col('path'),
            lit("/"),
            col('name')
        ).alias("initial_path"),
        concat(col("target.adlsGen2.location"), col("target.adlsGen2.subpath")).alias("initial_adls_path"),
        col("target.oneLake.workspaceId").alias("source_workspace_id"),
        col("target.oneLake.itemId").alias("source_lakehouse_id"),
        concat(
            lit("https://msit-onelake.dfs.fabric.microsoft.com/"),
            col("source_workspace_id"),
            lit("/"),
            col("source_lakehouse_id"),
            lit("/"),
            col('target.oneLake.path')
        ).alias("source_path"),
        col("Alias"),
        col("ModifiedTime")
    )

    if not shortcuts.rdd.isEmpty():
        shortcuts = shortcuts.dropDuplicates(["initial_workspace_id", "initial_lakehouse_id", "ShortcutName"])
        shortcuts = shortcuts.filter(col("initial_workspace_id").isNotNull())

        shortcuts.write.format("delta").mode("overwrite").saveAsTable("oct_shortcuts_stage")

        error_schema = StructType([
            StructField("WorkspaceID", StringType(), True),
            StructField("Type", StringType(), True),
            StructField("LakehouseID", StringType(), True),
            StructField("Message", StringType(), True),
            StructField("Alias", StringType(), True),
            StructField("ModifiedTime", TimestampType(), True)
        ])
        shortcuts_errors = spark.createDataFrame(final_results, error_schema)
        shortcuts_errors = shortcuts_errors.select(
            col("WorkspaceID").alias("Workspace_ID"),
            col("Type").alias("Item_Type"),
            col("LakehouseID").alias("Item_ID"),
            col("Message").alias("Error_Message"),
            col("Alias"),
            col("ModifiedTime")
        )

        if not shortcuts_errors.rdd.isEmpty():
            shortcuts_errors = shortcuts_errors.dropDuplicates()
            shortcuts_errors = shortcuts_errors.filter(col("Item_ID").isNotNull())
            shortcuts_errors.write.format("delta").mode("append").saveAsTable("oct_errors")

    final_lakehouse_names = final_list_lakehousenames()
    shortcuts_final = process_shortcuts()

    return shortcuts, shortcuts_errors


# In[36]:


def final_shortcuts(WorkspaceID,LakehouseID):
    spark.sql(f"delete from oct_shortcuts_stage where initial_lakehouse_id = '{LakehouseID}'")
    lakehouse_df = spark.sql(f"select WorkspaceID,ID from lakehouselist where WorkspaceID = '{WorkspaceID}' and ID = '{LakehouseID}'")
    final_results = nested_parallelize(lakehouse_df,final_results =[])
    shortcutsAPI_Schema = StructType([ StructField("name", StringType(), True),
                                                    StructField("path", StringType(), True),
                                                    StructField("target", StructType([StructField("type", StringType(), True), StructField("oneLake", StructType([StructField("itemId",StringType(), True), StructField("path",StringType(), True), StructField("workspaceId",StringType(), True)]), True),StructField("adlsGen2", StructType([StructField("connectionId",StringType(), True), StructField("location",StringType(), True), StructField("subpath",StringType(), True)]), True) ]), True),
                                                    StructField("initial_workspace_id", StringType(), True),
                                                    StructField("initial_lakehouse_id", StringType(), True),
                                                    StructField("Alias", StringType(), True),
                                                    StructField("ModifiedTime", TimestampType(), True),
                            ])
    shortcuts = spark.createDataFrame(final_results,shortcutsAPI_Schema)
    shortcuts = shortcuts.withColumn("ShortcutName",concat(when(col("path").contains("/Tables/"),concat(regexp_replace(col("path"), "/Tables/", ""), lit("."))).when(col("path").contains("/Tables"),concat(regexp_replace(col("path"), "/Tables", "dbo"), lit("."))).otherwise(lit("")),col("name"))) \
                        .select(col("initial_workspace_id"),
                                            col("initial_lakehouse_id"),
                                            col("ShortcutName"),
                                            concat(lit("https://msit-onelake.dfs.fabric.microsoft.com/"), col("initial_workspace_id"),lit("/") ,col("initial_lakehouse_id"),col('path'),lit("/"),col('name')).alias("initial_path"),
                                            concat(col("target.adlsGen2.location"),col("target.adlsGen2.subpath")).alias("initial_adls_path"),
                                            col("target.oneLake.workspaceId").alias("source_workspace_id"),
                                            col("target.oneLake.itemId").alias("source_lakehouse_id"),
                                            concat(lit("https://msit-onelake.dfs.fabric.microsoft.com/"),col("source_workspace_id"),lit("/"),col("source_lakehouse_id"),lit("/"),col('target.oneLake.path')).alias("source_path"),
                                            col("Alias"),
                                            col("ModifiedTime")
                                            )
    
    if not(shortcuts.isEmpty()):
        shortcuts = shortcuts.dropDuplicates()
        shortcuts = shortcuts.filter(col("initial_workspace_id").isNotNull())
        insert_update_stage_oct(spark_df = shortcuts, oct_table_name = 'oct_shortcuts_stage', on_name = 'initial_lakehouse_id', errors_flag="No",error_type = "NA")
    error_schema = StructType([
                StructField("WorkspaceID", StringType(), True),
                StructField("Type", StringType(), True),
                StructField("LakehouseID", StringType(), True),
                StructField("Message", StringType(), True),
                StructField("Alias", StringType(), True),
                StructField("ModifiedTime", TimestampType(), True)
            ])
    shortcuts_errors = spark.createDataFrame(final_results,error_schema)
    shortcuts_errors = shortcuts_errors.select(col("WorkspaceID").alias("Workspace_ID"), col("Type").alias("Item_Type"), col("LakehouseID").alias("Item_ID"), col("Message").alias("Error_Message"), col("Alias"), col("ModifiedTime"))
    if shortcuts_errors.isEmpty():
        pass
    else:
        shortcuts_errors = shortcuts_errors.dropDuplicates()
        shortcuts_errors = shortcuts_errors.filter(col("Item_ID").isNotNull())
        shortcuts_errors.write.format("delta").mode("append").saveAsTable("oct_errors")
    final_lakehouse_names = final_list_lakehousenames()
    shortcuts_final = process_shortcuts()
    return shortcuts,shortcuts_errors


# In[37]:


def get_tmsl(Workspace,Dataset):
    tmsl_script = fabric.get_tmsl(Dataset,Workspace)
    tmsl_dict = json.loads(tmsl_script)
    return tmsl_dict


# In[38]:


def get_modelproperties(tmsl,WorkspaceID,DatasetID,Alias,ModifiedTime):
    try:
        schema_model =  StructType([
                        StructField("Workspace_ID", StringType(), True),   
                        StructField("DatasetID", StringType(), True),    
                        StructField("DatasetName", StringType(), True),
                        StructField("createdTimestamp", StringType(), True),
                        StructField("Last_Update", StringType(), True),    
                        StructField("Last_Schema_Update", StringType(), True),
                        StructField("Last_Processed", StringType(), True),
                        StructField("Alias", StringType(), True), 
                        StructField("ModifiedTime", TimestampType(), True)
                    ])
        model_name = tmsl.get('name','Unknown') 
        model_createdTimestamp = tmsl.get('createdTimestamp','')
        model_last_update = tmsl.get('lastUpdate','')
        model_last_schema_update = tmsl.get('lastSchemaUpdate','')
        model_last_processed = tmsl.get('lastProcessed','')
        spark_model = spark.createDataFrame([(WorkspaceID,DatasetID,model_name,str(convert_to_pst(model_createdTimestamp)),str(convert_to_pst(model_last_update)),str(convert_to_pst(model_last_schema_update)),str(convert_to_pst(model_last_processed)),Alias,ModifiedTime)],schema_model)
        error_schema = StructType([
                StructField("Workspace_ID", StringType(), True),
                StructField("Item_Type", StringType(), True),
                StructField("Item_ID", StringType(), True),
                StructField("Error_Message", StringType(), True),
                StructField("Alias", StringType(), True),
                StructField("ModifiedTime", TimestampType(), True)
            ])
        model_errors = spark.createDataFrame([],error_schema) 
    except FabricHTTPException as e:
        error_response = e.response.json()
        error_code = error_response.get("errorCode", "UnknownError")
        error_msg = error_response.get("message", "No message found")
        message = f"{error_code} - {error_msg}"
        error_schema = StructType([
                StructField("Workspace_ID", StringType(), True),
                StructField("Item_Type", StringType(), True),
                StructField("Item_ID", StringType(), True),
                StructField("Error_Message", StringType(), True),
                StructField("Alias", StringType(), True),
                StructField("ModifiedTime", TimestampType(), True)
            ])
        model_errors = spark.createDataFrame([(WorkspaceID, "modelproperties", DatasetID, str(message), Alias, ModifiedTime)],error_schema) 
        schema_model = StructType([
                        StructField("Workspace_ID", StringType(), True),   
                        StructField("DatasetID", StringType(), True),    
                        StructField("DatasetName", StringType(), True),
                        StructField("createdTimestamp", StringType(), True),
                        StructField("Last_Update", StringType(), True),    
                        StructField("Last_Schema_Update", StringType(), True),
                        StructField("Last_Processed", StringType(), True),
                        StructField("Alias", StringType(), True), 
                        StructField("ModifiedTime", TimestampType(), True)
                    ])
        spark_model = spark.createDataFrame([],schema_model)
    except Exception as e:
        message = str(e)
        error_schema = StructType([
                StructField("Workspace_ID", StringType(), True),
                StructField("Item_Type", StringType(), True),
                StructField("Item_ID", StringType(), True),
                StructField("Error_Message", StringType(), True),
                StructField("Alias", StringType(), True),
                StructField("ModifiedTime", TimestampType(), True)
            ])
        model_errors = spark.createDataFrame([(WorkspaceID, "modelproperties", DatasetID, str(message), Alias, ModifiedTime)],error_schema) 
        schema_model = StructType([
                        StructField("Workspace_ID", StringType(), True),   
                        StructField("DatasetID", StringType(), True),    
                        StructField("DatasetName", StringType(), True),
                        StructField("createdTimestamp", StringType(), True),
                        StructField("Last_Update", StringType(), True),    
                        StructField("Last_Schema_Update", StringType(), True),
                        StructField("Last_Processed", StringType(), True),
                        StructField("Alias", StringType(), True), 
                        StructField("ModifiedTime", TimestampType(), True)
                    ])
        spark_model = spark.createDataFrame([],schema_model)
    return spark_model,model_errors


# In[39]:


def get_relationships(tmsl,WorkspaceID,DatasetID,Alias,ModifiedTime):
    try:
        schema_relationships = StructType([
                        StructField("Workspace_ID", StringType(), True),   
                        StructField("DatasetID", StringType(), True),    
                        StructField("Name", StringType(), True),
                        StructField("FromTable", StringType(), True),
                        StructField("FromColumn", StringType(), True),    
                        StructField("ToTable", StringType(), True),
                        StructField("ToColumn", StringType(), True),
                        StructField("State", StringType(), True),
                        StructField("CrossFilteringBehavior", StringType(), True),
                        StructField("SecurityFilteringBehavior", StringType(), True),
                        StructField("Active", StringType(), True),
                        StructField("Multiplicity", StringType(), True),
                        StructField("RelationshipModifiedTime", StringType(), True),
                        StructField("RefreshedTime", StringType(), True),
                        StructField("Alias", StringType(), True), 
                        StructField("ModifiedTime", TimestampType(), True)
                    ])
        model = tmsl.get('model',{})
        relationships = model.get('relationships',[])
        relationships_list = []
        for relindex in range(len(relationships)):
                relationship = relationships[relindex]
                RelationshipName = relationship.get('name','')
                fromTable = relationship.get('fromTable','')
                fromColumn = relationship.get('fromColumn','')
                toTable = relationship.get('toTable','')
                toColumn = relationship.get('toColumn','')
                state = relationship.get('state','')
                crossFilteringBehavior = relationship.get('crossFilteringBehavior','OneDirection')
                SecurityFilteringBehavior = relationship.get('securityFilteringBehavior','OneDirection')
                Active = relationship.get('isActive','true')
                toCardinality = relationship.get('toCardinality','one') 
                fromCardinality =relationship.get('fromCardinality','many')
                Multiplicity = fromCardinality + " to " + toCardinality
                modifiedTime = relationship.get('modifiedTime','')
                refreshedTime = relationship.get('refreshedTime','')
                relationships_list_stage = [(WorkspaceID,DatasetID,RelationshipName,fromTable,fromColumn,toTable,toColumn,state,crossFilteringBehavior,SecurityFilteringBehavior,Active,Multiplicity,str(convert_to_pst(modifiedTime)),str(convert_to_pst(refreshedTime)),Alias,ModifiedTime)]
                relationships_list = relationships_list + relationships_list_stage
        spark_relationships = spark.createDataFrame(relationships_list,schema_relationships)
        error_schema = StructType([
                StructField("Workspace_ID", StringType(), True),
                StructField("Item_Type", StringType(), True),
                StructField("Item_ID", StringType(), True),
                StructField("Error_Message", StringType(), True),
                StructField("Alias", StringType(), True),
                StructField("ModifiedTime", TimestampType(), True)
            ])
        relationship_errors = spark.createDataFrame([],error_schema) 
    except FabricHTTPException as e:
        error_response = e.response.json()
        error_code = error_response.get("errorCode", "UnknownError")
        error_msg = error_response.get("message", "No message found")
        message = f"{error_code} - {error_msg}"
        error_schema = StructType([
                StructField("Workspace_ID", StringType(), True),
                StructField("Item_Type", StringType(), True),
                StructField("Item_ID", StringType(), True),
                StructField("Error_Message", StringType(), True),
                StructField("Alias", StringType(), True),
                StructField("ModifiedTime", TimestampType(), True)
            ])
        relationship_errors = spark.createDataFrame([(WorkspaceID, "relationships", DatasetID, str(message), Alias, ModifiedTime)],error_schema) 
        schema_relationships = StructType([
                StructField("Workspace_ID", StringType(), True),   
                StructField("DatasetID", StringType(), True),    
                StructField("Name", StringType(), True),
                StructField("FromTable", StringType(), True),
                StructField("FromColumn", StringType(), True),    
                StructField("ToTable", StringType(), True),
                StructField("ToColumn", StringType(), True),
                StructField("State", StringType(), True),
                StructField("CrossFilteringBehavior", StringType(), True),
                StructField("SecurityFilteringBehavior", StringType(), True),
                StructField("Active", StringType(), True),
                StructField("Multiplicity", StringType(), True),
                StructField("RelationshipModifiedTime", StringType(), True),
                StructField("RefreshedTime", StringType(), True),
                StructField("Alias", StringType(), True), 
                StructField("ModifiedTime", TimestampType(), True)
            ])
        spark_relationships = spark.createDataFrame([],schema_relationships)
    except Exception as e:
        message = str(e)
        error_schema = StructType([
                StructField("Workspace_ID", StringType(), True),
                StructField("Item_Type", StringType(), True),
                StructField("Item_ID", StringType(), True),
                StructField("Error_Message", StringType(), True),
                StructField("Alias", StringType(), True),
                StructField("ModifiedTime", TimestampType(), True)
            ])
        relationship_errors = spark.createDataFrame([(WorkspaceID, "relationships", DatasetID, str(message), Alias, ModifiedTime)],error_schema) 
        schema_relationships = StructType([
                StructField("Workspace_ID", StringType(), True),   
                StructField("DatasetID", StringType(), True),    
                StructField("Name", StringType(), True),
                StructField("FromTable", StringType(), True),
                StructField("FromColumn", StringType(), True),    
                StructField("ToTable", StringType(), True),
                StructField("ToColumn", StringType(), True),
                StructField("State", StringType(), True),
                StructField("CrossFilteringBehavior", StringType(), True),
                StructField("SecurityFilteringBehavior", StringType(), True),
                StructField("Active", StringType(), True),
                StructField("Multiplicity", StringType(), True),
                StructField("RelationshipModifiedTime", StringType(), True),
                StructField("RefreshedTime", StringType(), True),
                StructField("Alias", StringType(), True), 
                StructField("ModifiedTime", TimestampType(), True)
            ])
        spark_relationships = spark.createDataFrame([],schema_relationships)
    return spark_relationships,relationship_errors


# In[40]:


def get_roles(tmsl,WorkspaceID,DatasetID,Alias,ModifiedTime):
    try:
        schema_role = StructType([
                        StructField("Workspace_ID", StringType(), True),   
                        StructField("DatasetID", StringType(), True),    
                        StructField("RoleName", StringType(), True),
                        StructField("RoleModelPermission", StringType(), True),
                        StructField("RoleModifiedTime", StringType(), True),    
                        StructField("TableName", StringType(), True),
                        StructField("TableFilterExpression", StringType(), True),
                        StructField("TablemodifiedTime", StringType(), True),
                        StructField("Alias", StringType(), True), 
                        StructField("ModifiedTime", TimestampType(), True)
                    ]) 
        model = tmsl.get('model',{})   
        roles = model.get('roles',[])
        roles_list = []
        for roleindex in range(len(roles)):
            role = roles[roleindex]
            rolename = role.get('name','Unknown')
            rolemodelpermission = role.get('modelPermission','Unknown')
            rolemodifiedTime= role.get('modifiedTime','Unknown')
            rolemembers = role.get('members',[])
            tablePermissions = role.get('tablePermissions',[])
            if len(tablePermissions)>0:
                for tablepermissionindex in range(len(tablePermissions)):
                    tablepermissionname = tablePermissions[tablepermissionindex].get('name','')
                    tablepermissionfilterExpression = tablePermissions[tablepermissionindex].get('filterExpression','')
                    tablepermissionmodifiedTime = tablePermissions[tablepermissionindex].get('modifiedTime','')
                roles_list_stage = [(WorkspaceID,DatasetID,rolename,rolemodelpermission,str(convert_to_pst(rolemodifiedTime)),tablepermissionname,tablepermissionfilterExpression,str(convert_to_pst(tablepermissionmodifiedTime)),Alias,ModifiedTime)]
            else:
                roles_list_stage = [(WorkspaceID,DatasetID,rolename,rolemodelpermission,str(convert_to_pst(rolemodifiedTime)),"Not Applicable","Not Applicable","Not Applicable",Alias,ModifiedTime)]
            roles_list = roles_list + roles_list_stage
        spark_roles = spark.createDataFrame(roles_list,schema_role)
        error_schema = StructType([
                StructField("Workspace_ID", StringType(), True),
                StructField("Item_Type", StringType(), True),
                StructField("Item_ID", StringType(), True),
                StructField("Error_Message", StringType(), True),
                StructField("Alias", StringType(), True),
                StructField("ModifiedTime", TimestampType(), True)
            ])
        role_errors = spark.createDataFrame([],error_schema) 
    except FabricHTTPException as e:
        error_response = e.response.json()
        error_code = error_response.get("errorCode", "UnknownError")
        error_msg = error_response.get("message", "No message found")
        message = f"{error_code} - {error_msg}"
        error_schema = StructType([
                StructField("Workspace_ID", StringType(), True),
                StructField("Item_Type", StringType(), True),
                StructField("Item_ID", StringType(), True),
                StructField("Error_Message", StringType(), True),
                StructField("Alias", StringType(), True),
                StructField("ModifiedTime", TimestampType(), True)
            ])
        role_errors = spark.createDataFrame([(WorkspaceID, "roles", DatasetID, str(message), Alias, ModifiedTime)],error_schema) 
        schema_role = StructType([
                StructField("Workspace_ID", StringType(), True),   
                StructField("DatasetID", StringType(), True),    
                StructField("RoleName", StringType(), True),
                StructField("RoleModelPermission", StringType(), True),
                StructField("RoleModifiedTime", StringType(), True),    
                StructField("TableName", StringType(), True),
                StructField("TableFilterExpression", StringType(), True),
                StructField("TablemodifiedTime", StringType(), True),
                StructField("Alias", StringType(), True), 
                StructField("ModifiedTime", TimestampType(), True)
            ]) 
        spark_roles = spark.createDataFrame([],schema_role)
    except Exception as e:
        message = str(e)
        error_schema = StructType([
                StructField("Workspace_ID", StringType(), True),
                StructField("Item_Type", StringType(), True),
                StructField("Item_ID", StringType(), True),
                StructField("Error_Message", StringType(), True),
                StructField("Alias", StringType(), True),
                StructField("ModifiedTime", TimestampType(), True)
            ])
        role_errors = spark.createDataFrame([(WorkspaceID, "roles", DatasetID, str(message), Alias, ModifiedTime)],error_schema) 
        schema_role = StructType([
                StructField("Workspace_ID", StringType(), True),   
                StructField("DatasetID", StringType(), True),    
                StructField("RoleName", StringType(), True),
                StructField("RoleModelPermission", StringType(), True),
                StructField("RoleModifiedTime", StringType(), True),    
                StructField("TableName", StringType(), True),
                StructField("TableFilterExpression", StringType(), True),
                StructField("TablemodifiedTime", StringType(), True),
                StructField("Alias", StringType(), True), 
                StructField("ModifiedTime", TimestampType(), True)
            ]) 
        spark_roles = spark.createDataFrame([],schema_role)
    return spark_roles,role_errors


# In[41]:


def extract_right_of_dot(s):
    if "." in s:
        newstring = s.split(".", 1)[1]
    else:
        newstring = s
    return newstring


# In[42]:


def clean_text(text):
    new_string = text.replace("[", "")
    new_string = new_string.replace("]", "")
    new_string = new_string.split('#')[0].strip()
    new_string = new_string.split(')')[0].strip()
    return new_string


# In[43]:


def get_table_columns(tmsl,WorkspaceID,DatasetID,Alias,ModifiedTime):
    try:
        model = tmsl.get('model',{}) 
        tables = model.get('tables',"NA")
        columns_list = []
        schema_columns = StructType([
                                StructField("Workspace_ID", StringType(), True),   
                                StructField("Dataset_ID", StringType(), True),    
                                StructField("Table_Name", StringType(), True),
                                StructField("Column_Name", StringType(), True),
                                StructField("Data_Type", StringType(), True),       
                                StructField("Alias", StringType(), True), 
                                StructField("ModifiedTime", TimestampType(), True)
                            ])
        for tableproperty in tables:
            columns = tableproperty.get('columns','NA')
            if columns != 'NA':
                for colindex in range(len(columns)):
                    column_name = columns[colindex]["name"] if "name" in columns[colindex] else "Not Present"
                    column_datatype = columns[colindex]["dataType"] if "dataType" in columns[colindex] else "Not Present"
                    columns_list_stage = [(WorkspaceID,DatasetID,tableproperty.get('name','NA') ,column_name,column_datatype,Alias,ModifiedTime)]
                    columns_list = columns_list + columns_list_stage
        spark_columns = spark.createDataFrame(columns_list, schema_columns)
        error_schema = StructType([
                StructField("Workspace_ID", StringType(), True),
                StructField("Item_Type", StringType(), True),
                StructField("Item_ID", StringType(), True),
                StructField("Error_Message", StringType(), True),
                StructField("Alias", StringType(), True),
                StructField("ModifiedTime", TimestampType(), True)
            ])
        column_errors = spark.createDataFrame([],error_schema)
    except FabricHTTPException as e:
        error_response = e.response.json()
        error_code = error_response.get("errorCode", "UnknownError")
        error_msg = error_response.get("message", "No message found")
        message = f"{error_code} - {error_msg}"
        error_schema = StructType([
                StructField("Workspace_ID", StringType(), True),
                StructField("Item_Type", StringType(), True),
                StructField("Item_ID", StringType(), True),
                StructField("Error_Message", StringType(), True),
                StructField("Alias", StringType(), True),
                StructField("ModifiedTime", TimestampType(), True)
            ])
        column_errors = spark.createDataFrame([(WorkspaceID, "columns", DatasetID, str(message), Alias, ModifiedTime)],error_schema)
        schema_columns = StructType([
                    StructField("Workspace_ID", StringType(), True),   
                    StructField("Dataset_ID", StringType(), True),    
                    StructField("Table_Name", StringType(), True),
                    StructField("Column_Name", StringType(), True),
                    StructField("Data_Type", StringType(), True),       
                    StructField("Alias", StringType(), True), 
                    StructField("ModifiedTime", TimestampType(), True)
                ]) 
        spark_columns = spark.createDataFrame([],schema_columns)
    except Exception as e:
        message = str(e)
        error_schema = StructType([
                StructField("Workspace_ID", StringType(), True),
                StructField("Item_Type", StringType(), True),
                StructField("Item_ID", StringType(), True),
                StructField("Error_Message", StringType(), True),
                StructField("Alias", StringType(), True),
                StructField("ModifiedTime", TimestampType(), True)
            ])
        column_errors = spark.createDataFrame([(WorkspaceID, "columns", DatasetID, str(message), Alias, ModifiedTime)],error_schema) 
        schema_columns = StructType([
                    StructField("Workspace_ID", StringType(), True),   
                    StructField("Dataset_ID", StringType(), True),    
                    StructField("Table_Name", StringType(), True),
                    StructField("Column_Name", StringType(), True),
                    StructField("Data_Type", StringType(), True),       
                    StructField("Alias", StringType(), True), 
                    StructField("ModifiedTime", TimestampType(), True)
                ]) 
        spark_columns = spark.createDataFrame([],schema_columns)
    return spark_columns,column_errors


# In[44]:


def get_measures(tmsl,WorkspaceID,DatasetID,Alias,ModifiedTime):
    try:
        model = tmsl.get('model',{}) 
        tables = model.get('tables',"NA")
        measures_list = []
        schema_measures = StructType([
                        StructField("Workspace_ID", StringType(), True),   
                        StructField("Dataset_ID", StringType(), True),    
                        StructField("Table_Name", StringType(), True),
                        StructField("Measure_Name", StringType(), True),
                        StructField("Expression", StringType(), True),    
                        StructField("Description", StringType(), True),
                        StructField("Format", StringType(), True),
                        StructField("Alias", StringType(), True), 
                        StructField("ModifiedTime", TimestampType(), True)
                    ])
        for tableproperty in tables:
            measures = tableproperty.get('measures','NA')
            if measures != "NA":
                for measureindex in range(len(measures)):
                    measure_name = measures[measureindex]["name"] if "name" in measures[measureindex] else "Not Present"
                    measure_expression = measures[measureindex]["expression"] if "expression" in measures[measureindex] else "Not Present"
                    measure_description = measures[measureindex]["description"] if "description" in measures[measureindex] else ""
                    measure_format = measures[measureindex]["formatString"] if "formatString" in measures[measureindex] else ""
                    measures_list_stage = (WorkspaceID,DatasetID,tableproperty.get('name','NA'),measure_name,measure_expression,measure_description,measure_format,Alias,ModifiedTime)
                    mreasures_list = measures_list.append(measures_list_stage)
        spark_measures = spark.createDataFrame(measures_list, schema_measures)
        error_schema = StructType([
                StructField("Workspace_ID", StringType(), True),
                StructField("Item_Type", StringType(), True),
                StructField("Item_ID", StringType(), True),
                StructField("Error_Message", StringType(), True),
                StructField("Alias", StringType(), True),
                StructField("ModifiedTime", TimestampType(), True)
            ])
        measure_errors = spark.createDataFrame([],error_schema) 
    except FabricHTTPException as e:
        error_response = e.response.json()
        error_code = error_response.get("errorCode", "UnknownError")
        error_msg = error_response.get("message", "No message found")
        message = f"{error_code} - {error_msg}"
        error_schema = StructType([
                StructField("Workspace_ID", StringType(), True),
                StructField("Item_Type", StringType(), True),
                StructField("Item_ID", StringType(), True),
                StructField("Error_Message", StringType(), True),
                StructField("Alias", StringType(), True),
                StructField("ModifiedTime", TimestampType(), True)
            ])
        measure_errors = spark.createDataFrame([(WorkspaceID, "measures", DatasetID, str(message), Alias, ModifiedTime)],error_schema) 
        schema_measures = StructType([
                StructField("Workspace_ID", StringType(), True),   
                StructField("Dataset_ID", StringType(), True),    
                StructField("Table_Name", StringType(), True),
                StructField("Measure_Name", StringType(), True),
                StructField("Expression", StringType(), True),    
                StructField("Description", StringType(), True),
                StructField("Format", StringType(), True),
                StructField("Alias", StringType(), True), 
                StructField("ModifiedTime", TimestampType(), True)
            ]) 
        spark_measures = spark.createDataFrame([],schema_measures)
    except Exception as e:
        message = str(e)
        error_schema = StructType([
                StructField("Workspace_ID", StringType(), True),
                StructField("Item_Type", StringType(), True),
                StructField("Item_ID", StringType(), True),
                StructField("Error_Message", StringType(), True),
                StructField("Alias", StringType(), True),
                StructField("ModifiedTime", TimestampType(), True)
            ])
        measure_errors = spark.createDataFrame([(WorkspaceID, "measures", DatasetID, str(message), Alias, ModifiedTime)],error_schema) 
        schema_measures = StructType([
                StructField("Workspace_ID", StringType(), True),   
                StructField("Dataset_ID", StringType(), True),    
                StructField("Table_Name", StringType(), True),
                StructField("Measure_Name", StringType(), True),
                StructField("Expression", StringType(), True),    
                StructField("Description", StringType(), True),
                StructField("Format", StringType(), True),
                StructField("Alias", StringType(), True), 
                StructField("ModifiedTime", TimestampType(), True)
            ]) 
        spark_measures = spark.createDataFrame([],schema_measures)
    return spark_measures,measure_errors


# In[45]:


def get_expressions(tmsl, WorkspaceID, DatasetID, Alias, ModifiedTime):
    try:
        model = tmsl.get('model', {}) 
        express = model.get("expressions", [])

        schema_expressions = StructType([
            StructField("Workspace_ID", StringType(), True),   
            StructField("Dataset_ID", StringType(), True),    
            StructField("Name", StringType(), True),
            StructField("Expression", StringType(), True),
            StructField("Alias", StringType(), True), 
            StructField("ModifiedTime", TimestampType(), True)
        ])

        expression_list = []

        if express:
            for expression_dict in express:
                expression_name = expression_dict.get("name")
                expression = expression_dict.get("expression")
                expression_list_stage = (WorkspaceID, DatasetID, expression_name, expression, Alias, ModifiedTime)
                expression_list.append(expression_list_stage)

        spark_expressions = spark.createDataFrame(expression_list, schema_expressions)
        error_schema = StructType([
                StructField("Workspace_ID", StringType(), True),
                StructField("Item_Type", StringType(), True),
                StructField("Item_ID", StringType(), True),
                StructField("Error_Message", StringType(), True),
                StructField("Alias", StringType(), True),
                StructField("ModifiedTime", TimestampType(), True)
            ])
        expressions_errors = spark.createDataFrame([],error_schema)
    except FabricHTTPException as e:
        error_response = e.response.json()
        error_code = error_response.get("errorCode", "UnknownError")
        error_msg = error_response.get("message", "No message found")
        message = f"{error_code} - {error_msg}"
        error_schema = StructType([
                StructField("Workspace_ID", StringType(), True),
                StructField("Item_Type", StringType(), True),
                StructField("Item_ID", StringType(), True),
                StructField("Error_Message", StringType(), True),
                StructField("Alias", StringType(), True),
                StructField("ModifiedTime", TimestampType(), True)
            ])
        expressions_errors = spark.createDataFrame([(WorkspaceID, "expressions", DatasetID, str(message), Alias, ModifiedTime)],error_schema) 
        schema_expressions = StructType([
                StructField("Workspace_ID", StringType(), True),   
                StructField("Dataset_ID", StringType(), True),    
                StructField("Name", StringType(), True),
                StructField("Expression", StringType(), True),
                StructField("Alias", StringType(), True), 
                StructField("ModifiedTime", TimestampType(), True)
            ]) 
        spark_expressions = spark.createDataFrame([],schema_expressions)
    except Exception as e:
        message = str(e)
        error_schema = StructType([
                StructField("Workspace_ID", StringType(), True),
                StructField("Item_Type", StringType(), True),
                StructField("Item_ID", StringType(), True),
                StructField("Error_Message", StringType(), True),
                StructField("Alias", StringType(), True),
                StructField("ModifiedTime", TimestampType(), True)
            ])
        expressions_errors = spark.createDataFrame([(WorkspaceID, "expressions", DatasetID, str(message), Alias, ModifiedTime)],error_schema) 
        schema_expressions = StructType([
                StructField("Workspace_ID", StringType(), True),   
                StructField("Dataset_ID", StringType(), True),    
                StructField("Name", StringType(), True),
                StructField("Expression", StringType(), True),
                StructField("Alias", StringType(), True), 
                StructField("ModifiedTime", TimestampType(), True)
            ]) 
        spark_expressions = spark.createDataFrame([],schema_expressions)
    return spark_expressions,expressions_errors


# In[46]:


import re
from pyspark.sql.types import StructType, StructField, StringType, TimestampType

from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Tables").getOrCreate()

def clean_text(s):
    # This helper function removes brackets and quotes from text
    return s.strip("[]\"")

def get_tables(tmsl, WorkspaceID, DatasetID, Alias, ModifiedTime):
    try:
        schema_tables = StructType([
            StructField("Workspace_ID", StringType(), True),
            StructField("Dataset_ID", StringType(), True),
            StructField("Mode", StringType(), True),
            StructField("Source_Type", StringType(), True),
            StructField("Expression", StringType(), True),
            StructField("Table_Name", StringType(), True),
            StructField("Source_Table_Name", StringType(), True),
            StructField("Alias", StringType(), True),
            StructField("ModifiedTime", TimestampType(), True)
        ])
        
        error_schema = StructType([
            StructField("Workspace_ID", StringType(), True),
            StructField("Item_Type", StringType(), True),
            StructField("Item_ID", StringType(), True),
            StructField("Error_Message", StringType(), True),
            StructField("Alias", StringType(), True),
            StructField("ModifiedTime", TimestampType(), True)
        ])
        
        model = tmsl.get('model', {})
        tables = model.get('tables', "NA")
        
        # New logic: Store all shared expressions for later reference
        shared_expressions = model.get('sharedExpressions', [])
        shared_expression_map = {expr.get('name'): expr.get('expression') for expr in shared_expressions}
        
        tables_list = []
        if tables == "NA":
            return spark.createDataFrame([], schema_tables), spark.createDataFrame([], error_schema)
        else:
            for tableproperty in tables:
                tableName = tableproperty.get('name', 'NA')
                partitions = tableproperty.get('partitions', ['NA'])
                partitions = partitions[0]
                if partitions == "NA":
                    pass
                else:
                    mode = partitions.get("mode", "Default")
                    source = partitions.get("source", "NA")
                    if source == "NA":
                        pass
                    else:
                        expression = source.get("expression", 'NA')
                        expression_type = source.get("type", 'NA')
                        source_type = "Notdefined"
                        source_table_name = "Notdefined"

                        # --- SURGICAL FIX FOR SHARED EXPRESSIONS ---
                        shared_expr_and_table_pattern = r'let\s+Source\s*=\s*([a-zA-Z0-9_]+).*?\[Schema\s*=\s*\"(.*?)\"\s*,\s*Item\s*=\s*\"(.*?)\"\]'
                        shared_match = re.search(shared_expr_and_table_pattern, expression, re.DOTALL)
                        
                        if shared_match:
                            shared_name = shared_match.group(1)
                            schema_name = shared_match.group(2)
                            item_name = shared_match.group(3)

                            # Determine source type from the shared expression's content
                            if shared_name in shared_expression_map and 'Sql.Database' in shared_expression_map[shared_name]:
                                source_type = "SQL Server Database (via shared expression)"
                            else:
                                source_type = "SQL Server Database" # Default fallback
                            
                            source_table_name = f"{schema_name}.{item_name}"
                        # The original if/elif chain now only runs if the surgical fix didn't apply
                        elif expression_type == "calculated":
                            source_table_name = "Calculated in model"
                            source_type = "Power BI/Semantic Model"
                        elif "entityName" in source:
                            source_type = "Microsoft Fabric"
                            source_table_name = source.get("schemaName", 'dbo') + '.' + source.get("entityName", 'NA')
                            expression = source.get("expressionSource", "NA")
                        elif 'Sql.Database' in expression:
                            source_type = "SQL Server Database"
                            # Existing logic to find table name directly in expression
                            schema_item_match = re.search(r'\[Schema\s*=\s*\"(.*?)\"\s*,\s*Item\s*=\s*\"(.*?)\"\]', expression)
                            if schema_item_match:
                                source_table_name = f"{schema_item_match.group(1)}.{schema_item_match.group(2)}"
                            elif 'Item=\"' in expression:
                                if 'Schema=\"' in expression:
                                    source_table_name = expression.split('Schema=\"')[1].split('"')[0] + '.' + expression.split('Item=\"')[1].split('"')[0]
                                else:
                                    source_table_name = 'dbo.' + expression.split('Item=\"')[1].split('"')[0]
                            elif 'Query=\"' in expression:
                                pattern1 = r'(?<=\bFROM)\s+(\w+\S*)'
                                pattern2 = r'(?<=\bJOIN)\s+(\w+\S*)'
                                pattern3 = r'(delta\.\s+)(\S+)+'
                                pattern4 = r'(parquet\.\s+)(\S+)+'
                                pattern5 = r'(?<=\bfrom)\s+(\[\w+\S*)'
                                pattern6 = r'(?<=\bjoin)\s+(\[\w+\S*)'
                                Query = expression.split('Query=\"')[1].split('"]')[0]
                                source_table_name_list = re.findall(pattern1, Query, re.IGNORECASE) + re.findall(pattern2, Query, re.IGNORECASE) + re.findall(pattern3, Query, re.IGNORECASE) + re.findall(pattern4, Query, re.IGNORECASE) + re.findall(pattern5, Query, re.IGNORECASE) + re.findall(pattern6, Query, re.IGNORECASE)
                                source_table_name = [clean_text(s) for s in source_table_name_list]
                            elif 'Navigation = Source{[Schema = \"' in expression:
                                schema_name = expression.split('Navigation = Source{[Schema = \"')[1].split('"')[0]
                                if 'Item = \"' in expression:
                                    source_table_name = expression.split('Item = \"')[1].split('"')[0]
                                    source_table_name = schema_name + "." + source_table_name
                                else:
                                    source_table_name = "Item not found"
                            elif 'Schema = "' in expression and 'Item = "' in expression:
                                schema_name = re.search(r'Schema\s*=\s*\"(.*?)\"', expression)
                                item_name = re.search(r'Item\s*=\s*\"(.*?)\"', expression)
                                if schema_name and item_name:
                                    source_table_name = f"{schema_name.group(1)}.{item_name.group(1)}"
                                else:
                                    source_table_name = "Not Found"
                            else:
                                source_table_name = "Not Found"
                        elif 'StaticTable' in expression or 'Row(\"' in expression or 'Table.FromRows(' in expression:
                            source_table_name = 'StaticTable'
                            source_type = 'StaticTable'
                        elif 'Navigation = Source{[Name = \"' in expression:
                            source_table_name = expression.split('Navigation = Source{[Name = \"')[1].split('"')[0]
                            source_type = "Azure" if 'AzureStorage.DataLake' in expression else "Naviagation type Not Defined in code"
                        elif 'Json.Document(Binary.Decompress(Binary.FromText(\"' in expression:
                            source_table_name = "binary Json Document"
                            source_type = "binary Json Document"
                        elif 'Excel.Workbook(File.Contents(\"' in expression:
                            source_table_name = expression.split('Excel.Workbook(File.Contents(\"')[1].split('"')[0]
                            source_type = "Excel Workbook"
                        elif 'Csv.Document(Web.Contents(\"' in expression:
                            source_table_name = expression.split('Csv.Document(Web.Contents(\"')[1].split('"')[0]
                            source_type = "Csv Document"
                        elif 'Source = DateTime.LocalNow()' in expression:
                            source_table_name = 'Calculated DateTime function'
                            source_type = "Calculated Datetime"
                        elif 'SharePoint.Tables(\"' in expression:
                            source_table_name = expression.split('SharePoint.Tables(\"')[1].split('"')[0]
                            source_type = "SharePoint"
                        elif 'Databricks.Catalogs(' in expression:
                            try:
                                source_table_name = re.findall(r'Name="(.*?)",Kind="Table"', expression)
                                source_table_name = source_table_name[0]
                                source_type = "Azure Databricks"
                            except Exception:
                                source_table_name = "Not Found"
                                source_type = "Azure Databricks"
                        elif 'Table.Combine({' in expression:
                            source_table_name = "Calculated in model"
                            source_type = "Table Combine"
                        elif expression_type == "calculationGroup":
                            source_table_name = "calculationGroup"
                            source_type = expression_type
                        elif 'AnalysisServices.Database' in expression:
                            source_table_name = 'Out of Scope'
                            source_type = 'Out of scope'
                        
                        # The very last fallback
                        else:
                            source_type = "Notdefined"
                            source_table_name = "Notdefined"

                        if isinstance(source_table_name, list):
                            for stname in source_table_name:
                                tables_list_stage = [(WorkspaceID, DatasetID, mode, source_type, expression, tableName, stname, Alias, ModifiedTime)]
                                tables_list.extend(tables_list_stage)
                        else:
                            tables_list_stage = [(WorkspaceID, DatasetID, mode, source_type, expression, tableName, source_table_name, Alias, ModifiedTime)]
                            tables_list.extend(tables_list_stage)
        
        spark_tables = spark.createDataFrame(tables_list, schema_tables)
        tables_errors = spark.createDataFrame([], error_schema)

    except FabricHTTPException as e:
        error_response = e.response.json()
        error_code = error_response.get("errorCode", "UnknownError")
        error_msg = error_response.get("message", "No message found")
        message = f"{error_code} - {error_msg}"
        tables_errors = spark.createDataFrame([(WorkspaceID, "tables", DatasetID, str(message), Alias, ModifiedTime)], error_schema)
        spark_tables = spark.createDataFrame([], schema_tables)
    except Exception as e:
        message = str(e)
        tables_errors = spark.createDataFrame([(WorkspaceID, "tables", DatasetID, str(message), Alias, ModifiedTime)], error_schema)
        spark_tables = spark.createDataFrame([], schema_tables)
    
    return spark_tables, tables_errors


# In[47]:


def get_dataset_lineage(WorkspaceID,DatasetID):
    try:
        Alias = get_executer_alias()
        ModifiedTime = get_modifiedtimestamp()
        tmsl = get_tmsl(Workspace = WorkspaceID,Dataset = DatasetID)
        functions = [
            get_modelproperties,
            get_relationships,
            get_roles,
            get_tables,
            get_table_columns,
            get_measures,
            get_expressions
        ]

        results = []
        with ThreadPoolExecutor(max_workers=7) as executor:
            # Submit functions in order and store futures in a list
            futures = [
                executor.submit(func, tmsl, WorkspaceID, DatasetID, Alias, ModifiedTime)
                for func in functions
            ]

            # Collect results in the same order as submitted
            for i, future in enumerate(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Error in 2 {functions[i].__name__}: {e}")
                    results.append(None) 
        #spark_model,spark_relationships,spark_roles,spark_tables,spark_columns,spark_measures,spark_expressions = tuple(results)
    except FabricHTTPException as e:
        results = []
        error_response = e.response.json()
        error_code = error_response.get("errorCode", "UnknownError")
        error_msg = error_response.get("message", "No message found")
        message = f"{error_code} - {error_msg}"
        schema_model =  StructType([
                        StructField("Workspace_ID", StringType(), True),   
                        StructField("DatasetID", StringType(), True),    
                        StructField("DatasetName", StringType(), True),
                        StructField("createdTimestamp", StringType(), True),
                        StructField("Last_Update", StringType(), True),    
                        StructField("Last_Schema_Update", StringType(), True),
                        StructField("Last_Processed", StringType(), True),
                        StructField("Alias", StringType(), True), 
                        StructField("ModifiedTime", TimestampType(), True)
                    ])
        schema_relationships = StructType([
                                StructField("Workspace_ID", StringType(), True),   
                                StructField("DatasetID", StringType(), True),    
                                StructField("Name", StringType(), True),
                                StructField("FromTable", StringType(), True),
                                StructField("FromColumn", StringType(), True),    
                                StructField("ToTable", StringType(), True),
                                StructField("ToColumn", StringType(), True),
                                StructField("State", StringType(), True),
                                StructField("CrossFilteringBehavior", StringType(), True),
                                StructField("SecurityFilteringBehavior", StringType(), True),
                                StructField("Active", StringType(), True),
                                StructField("Multiplicity", StringType(), True),
                                StructField("RelationshipModifiedTime", StringType(), True),
                                StructField("RefreshedTime", StringType(), True),
                                StructField("Alias", StringType(), True), 
                                StructField("ModifiedTime", TimestampType(), True)
                            ])
        schema_role = StructType([
                                StructField("Workspace_ID", StringType(), True),   
                                StructField("DatasetID", StringType(), True),    
                                StructField("RoleName", StringType(), True),
                                StructField("RoleModelPermission", StringType(), True),
                                StructField("RoleModifiedTime", StringType(), True),    
                                StructField("TableName", StringType(), True),
                                StructField("TableFilterExpression", StringType(), True),
                                StructField("TablemodifiedTime", StringType(), True),
                                StructField("Alias", StringType(), True), 
                                StructField("ModifiedTime", TimestampType(), True)
                            ])
        schema_columns = StructType([
                                        StructField("Workspace_ID", StringType(), True),   
                                        StructField("Dataset_ID", StringType(), True),    
                                        StructField("Table_Name", StringType(), True),
                                        StructField("Column_Name", StringType(), True),
                                        StructField("Data_Type", StringType(), True),       
                                        StructField("Alias", StringType(), True), 
                                        StructField("ModifiedTime", TimestampType(), True)
                                    ])
        schema_measures = StructType([
                                StructField("Workspace_ID", StringType(), True),   
                                StructField("Dataset_ID", StringType(), True),    
                                StructField("Table_Name", StringType(), True),
                                StructField("Measure_Name", StringType(), True),
                                StructField("Expression", StringType(), True),    
                                StructField("Description", StringType(), True),
                                StructField("Format", StringType(), True),
                                StructField("Alias", StringType(), True), 
                                StructField("ModifiedTime", TimestampType(), True)
                            ])
        schema_expressions = StructType([
                    StructField("Workspace_ID", StringType(), True),   
                    StructField("Dataset_ID", StringType(), True),    
                    StructField("Name", StringType(), True),
                    StructField("Expression", StringType(), True),
                    StructField("Alias", StringType(), True), 
                    StructField("ModifiedTime", TimestampType(), True)
                ])
        schema_tables = StructType([
                            StructField("Workspace_ID", StringType(), True),   
                            StructField("Dataset_ID", StringType(), True),    
                            StructField("Mode", StringType(), True),
                            StructField("Source_Type", StringType(), True), 
                            StructField("Expression", StringType(), True), 
                            StructField("Table_Name", StringType(), True), 
                            StructField("Source_Table_Name", StringType(), True), 
                            StructField("Alias", StringType(), True), 
                            StructField("ModifiedTime", TimestampType(), True)
                        ])
        error_schema = StructType([
                        StructField("Workspace_ID", StringType(), True),
                        StructField("Item_Type", StringType(), True),
                        StructField("Item_ID", StringType(), True),
                        StructField("Error_Message", StringType(), True),
                        StructField("Alias", StringType(), True),
                        StructField("ModifiedTime", TimestampType(), True)
                    ])
        spark_model = spark.createDataFrame([],schema_model)
        spark_relationships = spark.createDataFrame([],schema_relationships)
        spark_roles = spark.createDataFrame([],schema_role)
        spark_columns = spark.createDataFrame([],schema_columns)
        spark_measures = spark.createDataFrame([], schema_measures)
        spark_expressions = spark.createDataFrame([],schema_expressions)
        spark_tables = spark.createDataFrame([],schema_tables)
        model_errors = spark.createDataFrame([(WorkspaceID, "model", DatasetID, str(message), Alias, ModifiedTime)],error_schema)
        relationship_errors = spark.createDataFrame([],error_schema)
        roles_errors = spark.createDataFrame([],error_schema)
        tables_errors = spark.createDataFrame([],error_schema)
        columns_errors = spark.createDataFrame([],error_schema)
        measures_errors = spark.createDataFrame([],error_schema)
        expressions_errors =  spark.createDataFrame([],error_schema)
        results.append((spark_model,model_errors))
        results.append((spark_relationships,relationship_errors))
        results.append((spark_roles,roles_errors))
        results.append((spark_tables,tables_errors))
        results.append((spark_columns,columns_errors))
        results.append((spark_measures,measures_errors))
        results.append((spark_expressions,expressions_errors))
        print(message)
    except Exception as e:
        results = []
        message = str(e)
        schema_model =  StructType([
                        StructField("Workspace_ID", StringType(), True),   
                        StructField("DatasetID", StringType(), True),    
                        StructField("DatasetName", StringType(), True),
                        StructField("createdTimestamp", StringType(), True),
                        StructField("Last_Update", StringType(), True),    
                        StructField("Last_Schema_Update", StringType(), True),
                        StructField("Last_Processed", StringType(), True),
                        StructField("Alias", StringType(), True), 
                        StructField("ModifiedTime", TimestampType(), True)
                    ])
        schema_relationships = StructType([
                                StructField("Workspace_ID", StringType(), True),   
                                StructField("DatasetID", StringType(), True),    
                                StructField("Name", StringType(), True),
                                StructField("FromTable", StringType(), True),
                                StructField("FromColumn", StringType(), True),    
                                StructField("ToTable", StringType(), True),
                                StructField("ToColumn", StringType(), True),
                                StructField("State", StringType(), True),
                                StructField("CrossFilteringBehavior", StringType(), True),
                                StructField("SecurityFilteringBehavior", StringType(), True),
                                StructField("Active", StringType(), True),
                                StructField("Multiplicity", StringType(), True),
                                StructField("RelationshipModifiedTime", StringType(), True),
                                StructField("RefreshedTime", StringType(), True),
                                StructField("Alias", StringType(), True), 
                                StructField("ModifiedTime", TimestampType(), True)
                            ])
        schema_role = StructType([
                                StructField("Workspace_ID", StringType(), True),   
                                StructField("DatasetID", StringType(), True),    
                                StructField("RoleName", StringType(), True),
                                StructField("RoleModelPermission", StringType(), True),
                                StructField("RoleModifiedTime", StringType(), True),    
                                StructField("TableName", StringType(), True),
                                StructField("TableFilterExpression", StringType(), True),
                                StructField("TablemodifiedTime", StringType(), True),
                                StructField("Alias", StringType(), True), 
                                StructField("ModifiedTime", TimestampType(), True)
                            ])
        schema_columns = StructType([
                                        StructField("Workspace_ID", StringType(), True),   
                                        StructField("Dataset_ID", StringType(), True),    
                                        StructField("Table_Name", StringType(), True),
                                        StructField("Column_Name", StringType(), True),
                                        StructField("Data_Type", StringType(), True),       
                                        StructField("Alias", StringType(), True), 
                                        StructField("ModifiedTime", TimestampType(), True)
                                    ])
        schema_measures = StructType([
                                StructField("Workspace_ID", StringType(), True),   
                                StructField("Dataset_ID", StringType(), True),    
                                StructField("Table_Name", StringType(), True),
                                StructField("Measure_Name", StringType(), True),
                                StructField("Expression", StringType(), True),    
                                StructField("Description", StringType(), True),
                                StructField("Format", StringType(), True),
                                StructField("Alias", StringType(), True), 
                                StructField("ModifiedTime", TimestampType(), True)
                            ])
        schema_expressions = StructType([
                    StructField("Workspace_ID", StringType(), True),   
                    StructField("Dataset_ID", StringType(), True),    
                    StructField("Name", StringType(), True),
                    StructField("Expression", StringType(), True),
                    StructField("Alias", StringType(), True), 
                    StructField("ModifiedTime", TimestampType(), True)
                ])
        schema_tables = StructType([
                            StructField("Workspace_ID", StringType(), True),   
                            StructField("Dataset_ID", StringType(), True),    
                            StructField("Mode", StringType(), True),
                            StructField("Source_Type", StringType(), True), 
                            StructField("Expression", StringType(), True), 
                            StructField("Table_Name", StringType(), True), 
                            StructField("Source_Table_Name", StringType(), True), 
                            StructField("Alias", StringType(), True), 
                            StructField("ModifiedTime", TimestampType(), True)
                        ])
        error_schema = StructType([
                        StructField("Workspace_ID", StringType(), True),
                        StructField("Item_Type", StringType(), True),
                        StructField("Item_ID", StringType(), True),
                        StructField("Error_Message", StringType(), True),
                        StructField("Alias", StringType(), True),
                        StructField("ModifiedTime", TimestampType(), True)
                    ])
        spark_model = spark.createDataFrame([],schema_model)
        spark_relationships = spark.createDataFrame([],schema_relationships)
        spark_roles = spark.createDataFrame([],schema_role)
        spark_columns = spark.createDataFrame([],schema_columns)
        spark_measures = spark.createDataFrame([], schema_measures)
        spark_expressions = spark.createDataFrame([],schema_expressions)
        spark_tables = spark.createDataFrame([],schema_tables)
        model_errors = spark.createDataFrame([(WorkspaceID, "model", DatasetID, str(message), Alias, ModifiedTime)],error_schema)
        relationship_errors = spark.createDataFrame([],error_schema)
        roles_errors = spark.createDataFrame([],error_schema)
        tables_errors = spark.createDataFrame([],error_schema)
        columns_errors = spark.createDataFrame([],error_schema)
        measures_errors = spark.createDataFrame([],error_schema)
        expressions_errors =  spark.createDataFrame([],error_schema)
        results.append((spark_model,model_errors))
        results.append((spark_relationships,relationship_errors))
        results.append((spark_roles,roles_errors))
        results.append((spark_tables,tables_errors))
        results.append((spark_columns,columns_errors))
        results.append((spark_measures,measures_errors))
        results.append((spark_expressions,expressions_errors))
        print(message)
    return results


# In[48]:


def get_all_dataset_lineage():
    datasetlist_table = spark.sql("select * from datasetlist")
    spark_tables_list = []
    spark_expressions_list = []
    spark_columns_list = []
    spark_measures_list = []
    spark_relationships_list = []
    spark_model_list = []
    spark_roles_list = []
    spark_errors_list = []

    rows = datasetlist_table.select("WorkspaceID", "ID").collect()

    def lineage_task(row):
        WorkspaceID = row["WorkspaceID"]
        DatasetID = row["ID"]
        dataset_results = get_dataset_lineage(WorkspaceID=WorkspaceID, DatasetID=DatasetID)
        error_schema = StructType([
                    StructField("Workspace_ID", StringType(), True),
                    StructField("Item_Type", StringType(), True),
                    StructField("Item_ID", StringType(), True),
                    StructField("Error_Message", StringType(), True),
                    StructField("Alias", StringType(), True),
                    StructField("ModifiedTime", TimestampType(), True)
                ])
        errors = spark.createDataFrame([],error_schema)
        spark_model = dataset_results[0][0]
        model_errors = dataset_results[0][1]
        spark_relationships = dataset_results[1][0]
        relationship_errors = dataset_results[1][1]
        spark_roles = dataset_results[2][0]
        roles_errors = dataset_results[2][1]
        spark_tables = dataset_results[3][0]
        tables_errors = dataset_results[3][1]
        spark_columns = dataset_results[4][0]
        columns_errors = dataset_results[4][1]
        spark_measures = dataset_results[5][0]
        measures_errors = dataset_results[5][1]
        spark_expressions = dataset_results[6][0]
        expressions_errors = dataset_results[6][1]
        errors = errors.unionByName(model_errors)
        errors = errors.unionByName(relationship_errors)
        errors = errors.unionByName(roles_errors)
        errors = errors.unionByName(tables_errors)
        errors = errors.unionByName(columns_errors)
        errors = errors.unionByName(measures_errors)
        errors = errors.unionByName(expressions_errors)
        if not(spark_model.isEmpty()):
            spark_model= spark_model.dropDuplicates()
        if not(spark_relationships.isEmpty()):
            spark_relationships = spark_relationships.dropDuplicates()
        if not(spark_roles.isEmpty()):  
            spark_roles = spark_roles.dropDuplicates()  
        if not(spark_tables.isEmpty()):
            spark_tables = spark_tables.dropDuplicates()
        if not(spark_columns.isEmpty()):  
            spark_columns = spark_columns.dropDuplicates()  
        if not(spark_measures.isEmpty()):
            spark_measures = spark_measures.dropDuplicates()
        if not(spark_expressions.isEmpty()):  
            spark_expressions = spark_expressions.dropDuplicates()  
        if not(errors.isEmpty()):
            errors = errors.dropDuplicates()
        return spark_model,spark_relationships,spark_roles,spark_tables,spark_columns,spark_measures, spark_expressions,errors
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(lineage_task, rows))

    for (
        spark_model_stage,
        spark_relationships_stage,
        spark_roles_stage,
        spark_tables_stage,
        spark_columns_stage,
        spark_measures_stage,
        spark_expressions_stage,
        spark_errors_stage
    ) in results:
        spark_model_list.append(spark_model_stage)
        spark_relationships_list.append(spark_relationships_stage)
        spark_roles_list.append(spark_roles_stage)
        spark_tables_list.append(spark_tables_stage)
        spark_columns_list.append(spark_columns_stage)
        spark_measures_list.append(spark_measures_stage)
        spark_expressions_list.append(spark_expressions_stage)
        spark_errors_list.append(spark_errors_stage)

    
    spark_tables =  reduce(lambda df1, df2: df1.unionAll(df2), spark_tables_list)
    spark_expressions = reduce(lambda df1, df2: df1.unionAll(df2), spark_expressions_list)
    spark_columns = reduce(lambda df1, df2: df1.unionAll(df2), spark_columns_list)
    spark_measures = reduce(lambda df1, df2: df1.unionAll(df2), spark_measures_list)
    spark_relationships = reduce(lambda df1, df2: df1.unionAll(df2), spark_relationships_list)
    spark_model = reduce(lambda df1, df2: df1.unionAll(df2), spark_model_list)
    spark_roles = reduce(lambda df1, df2: df1.unionAll(df2), spark_roles_list)
    spark_errors = reduce(lambda df1, df2: df1.unionAll(df2), spark_errors_list)

    spark_model.write.format("delta").mode("overwrite").saveAsTable("oct_model_v1")
    spark_relationships.write.format("delta").mode("overwrite").saveAsTable("oct_relationships")
    spark_roles.write.format("delta").mode("overwrite").saveAsTable("oct_roles_v1")
    spark_tables.write.format("delta").mode("overwrite").saveAsTable("oct_tables")
    spark_columns.write.format("delta").mode("overwrite").saveAsTable("oct_column")
    spark_measures.write.format("delta").mode("overwrite").saveAsTable("oct_measures")
    spark_expressions.write.format("delta").mode("overwrite").saveAsTable("oct_expression")
    spark_errors.write.format("delta").mode("overwrite").saveAsTable("oct_errors")

    return "Operations Completed"


# In[49]:


def create_datasetlistv1_table():
    ps = spark.read.csv('Files/PowerBIDatasetInfo.csv', header=True)
    ds = spark.sql("""select lcase(trim(WorkspaceID)) as WorkspaceID,lcase(trim(ID)) as ID,Name,Alias,Info,ModifiedTime,concat("https://msit.powerbi.com/groups/",WorkspaceID,"/datasets/",ID,"/details?experience=power-bi") DatasetLink
     from datasetlist""")
    om = spark.sql("select *, CASE WHEN Last_Processed >= CURRENT_DATE - INTERVAL 30 DAY THEN 'Yes' ELSE 'No' END AS LastRefreshedFlag from oct_model_v1")
    ps = ps.alias("ps")
    ds = ds.alias("ds")
    om = om.alias("om")
    df = ds.join(ps, col("ds.ID") == col("ps.DatasetId"), "left") \
           .join(om, col("om.DatasetID") == col("ds.ID"), "left")
    df = df.select(
        col("ds.WorkspaceID").alias("WorkspaceID"),
        col("ds.ID").alias("DatasetID"),
        col("ds.Name").alias("Name"),
        col("ds.Alias").alias("ExecuterAlias"),
        col("ds.Info").alias("Info"),
        col("ds.DatasetLink").alias("DatasetLink"),
        col("ds.ModifiedTime").alias("ModifiedTime"),
        col("ps.ConfiguredBy").alias("ConfiguredBy"),
        col("ps.IsRefreshable").alias("IsRefreshable"), 
        col("om.createdTimestamp").alias("createdTimeStamp"),
        col("om.Last_Update").alias("LastUpdatedTime"),
        col("om.Last_Schema_Update").alias("LastSchemaUpdateTime"),
        col("om.Last_Processed").alias("LastProcessed"),
        col("om.LastRefreshedFlag").alias("LastRefreshedFlag")
    )

    df.write.format("delta").mode("overwrite").saveAsTable("datasetlistv1")
    return df


# In[50]:


def create_workspacelistv1_table():
    df = spark.sql("""
        SELECT *,
        concat("https://msit.powerbi.com/groups/",ID,"/list?experience=power-bi") as WorkSpaceLink
        FROM workspacelist""")

    df.write.format("delta").mode("overwrite").saveAsTable("workspacelistv1")
    return df


# In[51]:


def create_lakehouselistv1_table():
    df = spark.sql("""
        SELECT *,
        concat("https://msit.powerbi.com/groups/",WorkspaceID,"/lakehouses/",ID,"?experience=power-bi") as LakehouseLink
        FROM lakehouselist""")

    df.write.format("delta").mode("overwrite").saveAsTable("lakehouselistv1")
    return df


# In[4]:


def create_modetype_temp_view():
    df = spark.sql("""
        SELECT
            t.Dataset_ID,
            CASE
                WHEN MIN(t.Mode) = 'import' AND MAX(t.Mode) = 'import' THEN 'Import'
                WHEN MIN(t.Mode) = 'directLake' AND MAX(t.Mode) = 'directLake' THEN 'DirectLake'
                WHEN MIN(t.Mode) = 'directQuery' AND MAX(t.Mode) = 'directQuery' THEN 'DirectQuery'
                WHEN MIN(t.Mode) = 'Default' AND MAX(t.Mode) = 'Default' THEN 'Default'
                ELSE 'Hybrid'
            END AS Dataset_Mode_Status
        FROM
            oct_tables t
        GROUP BY
            t.Dataset_ID
    """)
    
    # Create or replace temp view
    df.createOrReplaceTempView("ModeType")
    return df


# In[53]:


def oct_measuresbridge():
    df = spark.sql("""
        SELECT Distinct ID as Dataset_ID from datasetlist  """)

    df.write.format("delta").mode("overwrite").saveAsTable("oct_measuresbridge")
    return df


# In[54]:


def save_msxitelemetry_details():

    daxstring = """
    EVALUATE
    SUMMARIZECOLUMNS(
    'Dim Report'[ApprovalStatus],
    'Dim Report'[GlobalURL],
    'Dim Report'[IsOSOTCertified],
    'Dim Report'[PBI_Source_FileName],
    'Dim Report'[PowerBIReportID],
    'Dim Report'[ReportID],
    'Dim Report'[ReportIsActive],
    'Dim Report'[ReportIsPublished],
    'Dim Report'[ReportName],
    'Dim Report'[ReportOwner],
    'Dim Report'[ReportType],
    'Dim Report'[SourceReportName],
    'Dim Report'[Workspace],
    'Dim Report'[IsBICoE Owned Report])
     ORDER BY 
    'Dim Report'[ApprovalStatus] ASC,
    'Dim Report'[GlobalURL] ASC,
    'Dim Report'[IsOSOTCertified] ASC,
    'Dim Report'[PBI_Source_FileName] ASC,
    'Dim Report'[PowerBIReportID] ASC,
    'Dim Report'[ReportID] ASC,
    'Dim Report'[ReportIsActive] ASC,
    'Dim Report'[ReportIsPublished] ASC,
    'Dim Report'[ReportName] ASC,
    'Dim Report'[ReportOwner] ASC,
    'Dim Report'[ReportType] ASC,
    'Dim Report'[SourceReportName] ASC,
    'Dim Report'[Workspace] ASC,
    'Dim Report'[IsBICoE Owned Report]
     /* END QUERY BUILDER */"""

    dataset = "MSXI 2.0 Telemetry"
    workspace = '*MSX Leader Insights'
    fabricdataframe = fabric.evaluate_dax(dataset=dataset, dax_string=daxstring, workspace=workspace)

    # Convert pandas DataFrame to Spark DataFrame
    dimreport_spark = spark.createDataFrame(fabricdataframe)
    dimreport_spark.createOrReplaceTempView("dimreport")

    spark.sql("""
    create or replace table msxitelemetry_details
    select 
    dr.`Dim Report[Workspace]` AS Workspace,
    dr.`Dim Report[ReportName]` as MSXIReportName,
    dr.`Dim Report[ReportID]` as MSXIReportID,
    dr.`Dim Report[ReportOwner]`AS ReportOwner,
    dr.`Dim Report[GlobalURL]` as MSXIReportURL,
    rt.PBISourceWorkspaceName,
    dr.`Dim Report[PowerBIReportID]`AS PowerBIReportID,
    dr.`Dim Report[PBI_Source_FileName]` AS PBISourceFileName,
    --rt.PBISourceReportName,
    rt.ReportURL as PBIReportURL,
    rt.APIreportid,
    rt.APIreportname,
    rt.datasetWorkspacename,
    rt.datasetid,
    rt.datasetname,
    dr.`Dim Report[IsBICoE Owned Report]` AS IsOSOTCertified,
    rt.ApprovalStatus
    from dimreport_table rt
    join  dimreport dr on  lcase( rt.ReportID) = lcase(dr.`Dim Report[ReportID]`)
    where dr.`Dim Report[IsBICoE Owned Report]` = 'Yes' and dr.`Dim Report[ReportIsPublished]` = 'True' and dr.`Dim Report[ReportIsActive]` = 'True'
        and lcase(dr.`Dim Report[ReportName]`) not like '%dummy%'  and dr.`Dim Report[ReportType]` = 'report' 
    Union All
    select 'NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA',ID as datasetid,'NA','NA','NA' from (
    select Distinct ID from datasetlist
    Except 
    select distinct rt.datasetid
    from dimreport_table rt
    join  dimreport dr on  lcase( rt.ReportID) = lcase(dr.`Dim Report[ReportID]`)
    where dr.`Dim Report[IsBICoE Owned Report]` = 'Yes' and dr.`Dim Report[ReportIsPublished]` = 'True' and dr.`Dim Report[ReportIsActive]` = 'True'
        and lcase(dr.`Dim Report[ReportName]`) not like '%dummy%'  and dr.`Dim Report[ReportType]` = 'report' )""")
 


# In[6]:


def save_factocttable():
    factoct_df = spark.sql("""
with cte_recommendedpath as
(
    select InitialLakehouseID,
    Initial_Shortcut_Name,
     case when Initial_Path in (
'https://msit-onelake.dfs.fabric.microsoft.com/d8bda4ab-adea-4e03-917d-157d82936d73/56a634be-4eaa-4aa2-a631-36b2fa248c0d/Files/CZDL/Sales/SalesAccounts/SalesAccounts/v1/dimaccountsummarygrouping'
,'https://msit-onelake.dfs.fabric.microsoft.com/d8bda4ab-adea-4e03-917d-157d82936d73/56a634be-4eaa-4aa2-a631-36b2fa248c0d/Files/CZDL/Sales/SalesAccounts/SalesAccounts/v1/dimcyallaccounts'  
,'https://msit-onelake.dfs.fabric.microsoft.com/751749de-3926-4c6d-bc7b-490f562ec6e1/43f53972-9b4b-4497-b48c-95eb72d0fed8/Tables/RLSCurated/ext_dimaccountrls_actualssecurity'
,'https://msit-onelake.dfs.fabric.microsoft.com/751749de-3926-4c6d-bc7b-490f562ec6e1/43f53972-9b4b-4497-b48c-95eb72d0fed8/Tables/RLSCurated/ext_dimaccountrls_targetsecurity')
OR Final_Source_Path in('https://msit-onelake.dfs.fabric.microsoft.com/d8bda4ab-adea-4e03-917d-157d82936d73/56a634be-4eaa-4aa2-a631-36b2fa248c0d/Files/CZDL/Sales/SalesAccounts/SalesAccounts/v1/dimaccountsummarygrouping'
,'https://msit-onelake.dfs.fabric.microsoft.com/d8bda4ab-adea-4e03-917d-157d82936d73/56a634be-4eaa-4aa2-a631-36b2fa248c0d/Files/CZDL/Sales/SalesAccounts/SalesAccounts/v1/dimcyallaccounts'  
,'https://msit-onelake.dfs.fabric.microsoft.com/751749de-3926-4c6d-bc7b-490f562ec6e1/43f53972-9b4b-4497-b48c-95eb72d0fed8/Tables/RLSCurated/ext_dimaccountrls_actualssecurity'
,'https://msit-onelake.dfs.fabric.microsoft.com/751749de-3926-4c6d-bc7b-490f562ec6e1/43f53972-9b4b-4497-b48c-95eb72d0fed8/Tables/RLSCurated/ext_dimaccountrls_targetsecurity')
then 'Yes' else 'No' End AS RecommendedFlag,
CASE
    WHEN Final_Shortcut_Name LIKE '%dimaccountsummarygrouping' THEN
        'https://msit-onelake.dfs.fabric.microsoft.com/d8bda4ab-adea-4e03-917d-157d82936d73/56a634be-4eaa-4aa2-a631-36b2fa248c0d/Files/CZDL/Sales/SalesAccounts/SalesAccounts/v1/dimaccountsummarygrouping'
       
    WHEN SPLIT(Initial_Shortcut_Name, '\\.')[1] LIKE '%dimaccountsummarygrouping_CZDL' THEN
        'https://msit-onelake.dfs.fabric.microsoft.com/d8bda4ab-adea-4e03-917d-157d82936d73/56a634be-4eaa-4aa2-a631-36b2fa248c0d/Files/CZDL/Sales/SalesAccounts/SalesAccounts/v1/dimaccountsummarygrouping'
       
    WHEN Final_Shortcut_Name LIKE '%dimcyallaccounts' THEN
        'https://msit-onelake.dfs.fabric.microsoft.com/d8bda4ab-adea-4e03-917d-157d82936d73/56a634be-4eaa-4aa2-a631-36b2fa248c0d/Files/CZDL/Sales/SalesAccounts/SalesAccounts/v1/dimcyallaccounts'
       
    WHEN SPLIT(Initial_Shortcut_Name, '\\.')[1] LIKE '%dimcyallaccounts_CZDL' THEN
        'https://msit-onelake.dfs.fabric.microsoft.com/d8bda4ab-adea-4e03-917d-157d82936d73/56a634be-4eaa-4aa2-a631-36b2fa248c0d/Files/CZDL/Sales/SalesAccounts/SalesAccounts/v1/dimcyallaccounts'
       
    WHEN Final_Shortcut_Name LIKE '%ext_dimaccountrls_targetsecurity' THEN
        'https://msit-onelake.dfs.fabric.microsoft.com/751749de-3926-4c6d-bc7b-490f562ec6e1/43f53972-9b4b-4497-b48c-95eb72d0fed8/Tables/RLSCurated/ext_dimaccountrls_targetsecurity'
       
    WHEN SPLIT(Initial_Shortcut_Name, '\\.')[1] LIKE '%RLS_TargetSecurity' THEN
        'https://msit-onelake.dfs.fabric.microsoft.com/751749de-3926-4c6d-bc7b-490f562ec6e1/43f53972-9b4b-4497-b48c-95eb72d0fed8/Tables/RLSCurated/ext_dimaccountrls_targetsecurity'
       
    WHEN Final_Shortcut_Name LIKE '%ext_dimaccountrls_actualssecurity' THEN
        'https://msit-onelake.dfs.fabric.microsoft.com/751749de-3926-4c6d-bc7b-490f562ec6e1/43f53972-9b4b-4497-b48c-95eb72d0fed8/Tables/RLSCurated/ext_dimaccountrls_actualssecurity'
       
    WHEN SPLIT(Initial_Shortcut_Name, '\\.')[1] LIKE '%RLS_ActualSecurity' THEN
        'https://msit-onelake.dfs.fabric.microsoft.com/751749de-3926-4c6d-bc7b-490f562ec6e1/43f53972-9b4b-4497-b48c-95eb72d0fed8/Tables/RLSCurated/ext_dimaccountrls_actualssecurity'
       
    ELSE ''
END AS RecommendedPath
from oct_shortcuts)
 
select distinct lcase(trim(t.Workspace_ID)) as Workspace_ID
    ,lcase(trim(t.Dataset_ID)) as Dataset_ID
    ,t.Mode
    ,CASE WHEN t.Source_Type = 'Out of scope' THEN 'Analysis Services' ELSE t.Source_Type END AS Source_Type
    ,t.Expression
    ,t.Table_Name
    ,t.source_table_name AS Source_Table_Name
    --,t.Source_Table_Name
    ,coalesce(s.InitialWorkspaceID,l.WorkspaceID) as InitialWorkspaceID
    ,coalesce(s.InitialLakehouseID,l.ID) as InitialLakehouseID
    ,coalesce(s.InitialLakehouseName,l.Name) as InitialLakehouseName
    ,coalesce(s.InitialLakehouseLink,concat("https://msit.powerbi.com/groups/",coalesce(s.InitialWorkspaceID,l.WorkspaceID),"/lakehouses/",coalesce(s.InitialLakehouseID,l.ID),"?experience=power-bi")) as InitialLakehouseLink
    ,s.Initial_Path
    ,s.Initial_abfsspath
    ,s.Initial_Shortcut_Name
    ,s.FinalSourceWorkspaceID
    ,s.FinalSourceLakehouseID
    ,s.FinalSourceLakehouseName
    ,s.FinalSourceLakehouseLink
    ,s.Final_Shortcut_Name
    ,s.Final_Source_Path
    ,s.Final_Source_abfsspath
    ,s.Source_ADLS_Path
    ,s.OSOTLakehouseFlag
    ,s.SourceLakehouseType
    ,s.Source_Area_Domain
    ,t.Alias as ExecutorAlias
    ,t.ModifiedTime as ExecutorModifiedTIme
    , M.Dataset_Mode_Status
    ,CASE WHEN instr(t.source_table_name, '.') > 0 THEN split(t.source_table_name, '\\.')[1]
            --When len(t.source_table_name) >=50 then 'Binary File'
            ELSE t.source_table_name END AS source_table_wo_schema
    ,CASE WHEN Final_Shortcut_Name LIKE '%dimaccountsummarygrouping' THEN 'Yes'
    WHEN Final_Shortcut_Name LIKE '%ext_dimaccountrls_actualssecurity' THEN 'Yes'
    WHEN Final_Shortcut_Name LIKE '%ext_dimaccountrls_targetsecurity' THEN 'Yes'
    WHEN Final_Shortcut_Name LIKE '%dimcyallaccounts' THEN 'Yes'  
  When SPLIT(s.Initial_Shortcut_Name, '\\.')[1]  like  '%RLS_TargetSecurity' THEN 'Yes'
  when SPLIT(s.Initial_Shortcut_Name, '\\.')[1] like  '%RLS_ActualSecurity' THEN 'Yes'
  when SPLIT(s.Initial_Shortcut_Name, '\\.')[1] like '%dimaccountsummarygrouping_CZDL' THEN 'Yes'
  when SPLIT(s.Initial_Shortcut_Name, '\\.')[1] like '%dimcyallaccounts_CZDL' THEN 'Yes'
        ELSE 'No'
         End as ALDAFlag,
          rp.RecommendedFlag,
          rp.RecommendedPath,
    case when rp.RecommendedFlag = 'No' then rp.RecommendedPath else  ' ' end as recommened_alda_path,
    CASE 
        WHEN os.DatasetID IS NOT NULL THEN 'Yes'
        ELSE 'No'
    END AS OCT_OSOT_Certification
from oct_tables t
left join oct_parameters p on lcase(trim(t.Dataset_ID)) = lcase(trim(p.DatasetID))
left join oct_shortcuts s on lcase(trim(t.Source_Table_Name)) = lcase(trim(s.Initial_Shortcut_Name))
and lcase(trim(p.LakehouseID)) = lcase(trim(s.InitialLakehouseID))
left join cte_recommendedpath rp on lcase(trim(t.Source_Table_Name)) = lcase(trim(rp.Initial_Shortcut_Name))
and lcase(trim(p.LakehouseID)) = lcase(trim(rp.InitialLakehouseID))
Left JOIN ModeType M ON LCASE(TRIM(t.Dataset_ID)) = LCASE(TRIM(M.Dataset_ID))
Left JOIN OCT_OSOT_Certification os on lcase(trim(t.Dataset_ID)) = lcase(trim(os.DatasetID))
left join lakehouselist l on lcase(trim(l.ID)) = lcase(trim(p.LakehouseID))""")
    factoct_df.write.format("delta").option("overwriteSchema", "true").mode("overwrite").saveAsTable("factoct")
    return factoct_df


# In[56]:


def DS_Published_Status():
    df = spark.sql("""
select 
    distinct dlv.Dataset_ID,
    CASE 
        WHEN dlv.Dataset_ID = dr.datasetId AND dr.datasetname<> 'NA' THEN 'Yes' 
        ELSE 'No' 
    END as IsMXSIPublishedDataset
from factoct dlv
left join msxitelemetry_details dr on dlv.Dataset_ID = dr.datasetId""")

    df.write.format("delta").mode("overwrite").saveAsTable("DS_Published_Status")
    return df


# In[57]:


def save_measures():
    spark.sql("""
    CREATE OR REPLACE Table OCT_Measures_Final
    AS SELECT om.*, mf.Definition,mf.Feedback, mf.Complex
    FROM oct_measures om
    left join ai_measure_definition mf on lcase(om.Workspace_ID) = lcase(mf.Workspace_ID)
    and lcase(om.Dataset_ID) = lcase(mf.Dataset_ID)
    and lcase(om.Table_Name) = lcase(mf.Table_Name)
    and lcase(om.Measure_Name) = lcase(mf.Measure_Name)""")


# In[1]:


def save_oct_roles_final():
  spark.sql("""CREATE OR REPLACE Table oct_roles_v1_Final
AS SELECT
orv.DatasetID || '|' || orv.TableName AS DatasetTableKey,
orv.Workspace_ID,
orv.DatasetID,
orv.RoleName,
orv.RoleModelPermission,
orv.RoleModifiedTime,
orv.TableName,
orv.TableFilterExpression,
air.TableFilterExpression_Definition,
orv.TablemodifiedTime,
orv.Alias,
orv.ModifiedTime
FROM oct_roles_v1 orv
left join ai_oct_roles_v1 air on lcase(orv.Workspace_ID) = lcase(air.Workspace_ID)
and lcase(orv.DatasetID) = lcase(air.DatasetID)
and lcase(orv.TableName) = lcase(air.TableName)
and lcase(orv.TableFilterExpression) = lcase(air.TableFilterExpression)""")


# In[59]:


def save_tables_without_relationship():
    spark.sql("""
CREATE OR REPLACE TABLE oct_tables_without_relationship 
SELECT  ct.Dataset_ID, ct.table_name
FROM oct_tables ct
WHERE NOT EXISTS (
    SELECT 1
    FROM oct_relationships r
    WHERE r.DatasetID = ct.Dataset_ID
      AND (r.FromTable = ct.Table_Name OR r.ToTable = ct.Table_Name)
) """)


# In[1]:


def save_oct_columnv1():
 df = spark.sql("""
 WITH PII_check AS (
    SELECT 
        Dataset_ID,
        Table_Name,
        Column_Name,
        CASE 
            WHEN LOWER(Column_Name) LIKE '%phone%' OR LOWER(Column_Name) LIKE '%address%' 
              OR LOWER(Column_Name) LIKE '%birth%' OR LOWER(Column_Name) LIKE '%personalemail%' 
              OR LOWER(Column_Name) = 'ssn' THEN "Yes" ELSE "No" END AS has_PII
    FROM oct_column
    WHERE LOWER(Data_Type) <> 'datetime'
      AND NOT (LOWER(Column_Name) LIKE 'is%' OR LOWER(Column_Name) LIKE 'has%' OR LOWER(Column_Name) LIKE '%count%'
    OR  LOWER(Column_Name) LIKE '%#%')
),
repeated_columns AS (
    SELECT 
        Dataset_ID,
        Column_Name,
        COUNT(DISTINCT Table_Name) AS table_count
    FROM oct_column
    GROUP BY Dataset_ID, Column_Name
    HAVING COUNT(DISTINCT Table_Name) > 1
)
SELECT 
    c.*,
    case when has_PII = 'Yes' then 'Yes' Else 'No' END AS has_PII,
    CASE 
        WHEN rc.table_count > 1 THEN 0
        ELSE 1
    END AS Duplicate_fields_in_Dataset,
    CASE 
        WHEN f.OSOTLakehouseFlag = 'Yes' THEN 'Yes' 
        WHEN f.OSOTLakehouseFlag = 'No' THEN 'No' 
        ELSE 'No' 
    END AS OSOTLakehouseFlag 
FROM oct_column c
LEFT JOIN PII_check pc ON c.Dataset_ID = pc.Dataset_ID AND c.Table_Name = pc.Table_Name  and c.Column_Name = pc.Column_Name
LEFT JOIN repeated_columns rc
    ON c.Dataset_ID = rc.Dataset_ID 
    AND c.Column_Name = rc.Column_Name
left JOIN factoct f 
    ON f.Table_Name = c.Table_Name 
    AND f.Dataset_ID = c.Dataset_ID """)
 df.write.mode("overwrite").option("mergeSchema", "true").saveAsTable("oct_columnv1")  


# In[1]:


def save_oct_TablesRLS():
    df = spark.sql("""
with actual_target_check as (
    SELECT 
        Dataset_ID,
        Table_Name,
        MAX(CASE 
            WHEN (LOWER(Column_Name) LIKE '%revenue%' OR LOWER(Column_Name) LIKE '%actual%' OR LOWER(Column_Name) LIKE '%acr%')
              AND LOWER(Column_Name) NOT LIKE '%revenuetarget%' AND lower(Column_Name) NOT LIKE '%budget%'
        AND lower(Column_Name) NOT LIKE '# The command is not a standard IPython magic command. It is designed for use within Fabric notebooks only.
# %pipeline%' AND lower(Column_Name) NOT LIKE '%forecast%' 
        AND  LOWER(Column_Name) NOT LIKE '%key' THEN 1 ELSE 0 END) AS has_actuals,
        MAX(CASE 
            WHEN LOWER(Column_Name) LIKE '%quota%' OR LOWER(Column_Name) LIKE '%target%' OR LOWER(Column_Name) LIKE '%revenuetarget%' THEN 1 ELSE 0 END) AS has_targets,
        MAX(CASE 
            WHEN LOWER(Column_Name) LIKE '%tpid%' OR LOWER(Column_Name) LIKE '%accountid%' OR LOWER(Column_Name) LIKE '%tpaccountid%' THEN 1 ELSE 0 END) AS has_accounts
    FROM oct_column
    WHERE LOWER(Data_Type) IN ('int64', 'double', 'decimal')
      AND NOT (LOWER(Column_Name) LIKE 'is%' OR LOWER(Column_Name) LIKE 'has%' OR LOWER(Column_Name) LIKE '%order'
      OR LOWER(Column_Name) LIKE '%type')
    GROUP BY Dataset_ID, Table_Name
),
 oct_roles as (
        select distinct DatasetID,TableName from oct_roles_v1_final
    )
    ,AppliedRLS as (
    select distinct a.DatasetID, a.TargetTable from oct_graph_relationships a
    join oct_roles b on a.DatasetID = b.DatasetID and a.SourceTable = b.TableName
    ) 
   SELECT distinct 
    c.Workspace_ID,
c.Dataset_ID,
        c.Table_Name,
        c.Dataset_ID || '|' || c.Table_Name AS DatasetTableKey,
       -- c.Column_Name,
   oc.has_actuals,
    oc.has_targets,
    oc.has_accounts,
        CASE WHEN oc.has_actuals = 1 OR oc.has_targets = 1 THEN 'Yes' ELSE 'No' 
    END AS Has_MSSales_Required,
    CASE WHEN (oc.has_actuals = 1 OR oc.has_targets = 1) AND oc.has_accounts = 1 THEN 'Yes' 
    ELSE 'No' END AS Has_accountAssignment_required,
    CASE WHEN (oc.has_actuals = 1 OR oc.has_targets = 1) AND oc.has_accounts = 1 THEN 'Yes' 
    ELSE 'No' END AS Has_ALDA_required,
    case when b.DatasetID is not null then "Yes" else "No" end as RLSApplied,
 CASE WHEN lower(f.Final_Shortcut_Name) LIKE '%dimaccountsummarygrouping' THEN 'Yes'
    WHEN lower(f.Final_Shortcut_Name) LIKE '%ext_dimaccountrls_actualssecurity' THEN 'Yes'
    WHEN lower(f.Final_Shortcut_Name) LIKE '%ext_dimaccountrls_targetsecurity' THEN 'Yes'
    WHEN lower(f.Final_Shortcut_Name) LIKE '%dimcyallaccounts' THEN 'Yes' 
    WHEN lower(Final_Shortcut_Name) LIKE '%proxy%'  THEN 'Yes'   
  When SPLIT(f.Initial_Shortcut_Name, '\\.')[1]  like  '%RLS_TargetSecurity' THEN 'Yes'
  when SPLIT(f.Initial_Shortcut_Name, '\\.')[1] like  '%RLS_ActualSecurity' THEN 'Yes'
  when SPLIT(f.Initial_Shortcut_Name, '\\.')[1] like '%dimaccountsummarygrouping_CZDL' THEN 'Yes'
  when SPLIT(f.Initial_Shortcut_Name, '\\.')[1] like '%dimcyallaccounts_CZDL' THEN 'Yes'
    WHEN SPLIT(f.Initial_Shortcut_Name, '\\.')[1] like '%proxy%' THEN 'Yes'
        ELSE 'No'
         End as SecurityFlag,
    CASE 
        WHEN f.OSOTLakehouseFlag = 'Yes' THEN 'Yes' 
        WHEN f.OSOTLakehouseFlag = 'No' THEN 'No' 
        ELSE 'No' 
    END AS OSOTLakehouseFlag 
FROM oct_column c
LEFT JOIN actual_target_check oc ON c.Dataset_ID = oc.Dataset_ID AND c.Table_Name = oc.Table_Name
left JOIN factoct f 
    ON f.Table_Name = c.Table_Name 
    AND f.Dataset_ID = c.Dataset_ID 
left join AppliedRLS b on c.Dataset_ID = b.DatasetID and c.Table_Name = b.TargetTable    
    """)
    df.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable("oct_TablesRLS_Check")


# In[62]:


def oct_graph_relationships():

    relationship_df = spark.sql("""select DatasetID, FromTable,FromColumn, ToTable, ToColumn, CrossFilteringBehavior, Multiplicity from oct_relationships""")
    graph_by_dataset = defaultdict(lambda: defaultdict(list))

    for row in relationship_df.collect():
        dataset_id = row['DatasetID']
        from_table = row['FromTable']
        to_table = row['ToTable']
        behavior = row['CrossFilteringBehavior']
        multiplicity = row['Multiplicity']

        graph = graph_by_dataset[dataset_id]

        if behavior == 'bothDirections':
            graph[from_table].append((to_table, 'bothDirections'))
            graph[to_table].append((from_table, 'bothDirections'))
        elif behavior == 'OneDirection' and multiplicity == 'many to one':
            graph[to_table].append((from_table, 'REVERSE'))

    results = []

    for dataset_id, graph in graph_by_dataset.items():
        for source_table in list(graph.keys()):  
            visited = set()
            queue = deque()
            queue.append((source_table, [source_table]))

            while queue:
                current, path = queue.popleft()

                if current in visited:
                    continue
                visited.add(current)

                for neighbor, direction in graph[current]:
                    if neighbor not in path:
                        new_path = path + [neighbor]
                        results.append((
                            dataset_id,
                            source_table,
                            neighbor,
                            direction,
                            " → ".join(new_path)
                        ))
                        queue.append((neighbor, new_path))
    schema = StructType([
        StructField("DatasetID", StringType(), True),
        StructField("SourceTable", StringType(), True),
        StructField("TargetTable", StringType(), True),
        StructField("Direction", StringType(), True),
        StructField("Path", StringType(), True),
    ])

    result_df = spark.createDataFrame(results, schema)
    roles_df = spark.table("oct_roles_v1_final")
    final_df = result_df.alias("gs") \
    .join(
        roles_df.alias("rf"),
        (col("gs.SourceTable") == col("rf.TableName")) &
        (col("gs.DatasetID") == col("rf.DatasetID")),
        how="inner"
    ) \
    .select("gs.*") \
    .withColumn("DatasetTableKey", concat_ws("|", col("gs.DatasetID").cast("string"), col("gs.SourceTable"))) \
    .distinct()
    final_df.write.format("delta").option("overwriteSchema", "true").mode("overwrite").saveAsTable("oct_graph_relationships")


# In[1]:


def oct_graph_relationships_bridge():
    df = spark.sql("""
        SELECT DISTINCT
            DatasetID,
            SourceTable,
            DatasetID || '|' || SourceTable AS DatasetTableKey
        FROM oct_graph_relationships
    """)
    df.write.mode("overwrite").saveAsTable("oct_graph_relationships_bridge")


# In[63]:


def refresh_dataset():
    try:
        refreshworkspace = "OCT"
        refreshdataset = "OCT Report"
        tmsl_model_refresh_script = {
            "refresh": {
                "type": "full",
                "objects": [
                    {
                        "database": refreshdataset,
                    }
                ]
            }
        }
        fabric.execute_tmsl(workspace=refreshworkspace, script=tmsl_model_refresh_script)
        msg = "refresh is triggered"
    except Exception as e: 
        msg = e
    return msg


# In[64]:


def final_optimize_tables():
    table_paths = [
        "abfss://ce1d0a35-d7f8-462c-895f-da3fb1d7f85f@msit-onelake.dfs.fabric.microsoft.com/75d21c50-d4ae-4778-98e3-41ec1f463ab5/Tables/datasetlistv1",
        "abfss://ce1d0a35-d7f8-462c-895f-da3fb1d7f85f@msit-onelake.dfs.fabric.microsoft.com/75d21c50-d4ae-4778-98e3-41ec1f463ab5/Tables/factoct",
        "abfss://ce1d0a35-d7f8-462c-895f-da3fb1d7f85f@msit-onelake.dfs.fabric.microsoft.com/75d21c50-d4ae-4778-98e3-41ec1f463ab5/Tables/lakehouselist",
        "abfss://ce1d0a35-d7f8-462c-895f-da3fb1d7f85f@msit-onelake.dfs.fabric.microsoft.com/75d21c50-d4ae-4778-98e3-41ec1f463ab5/Tables/lakehouselistv1",
        "abfss://ce1d0a35-d7f8-462c-895f-da3fb1d7f85f@msit-onelake.dfs.fabric.microsoft.com/75d21c50-d4ae-4778-98e3-41ec1f463ab5/Tables/oct_column",
        "abfss://ce1d0a35-d7f8-462c-895f-da3fb1d7f85f@msit-onelake.dfs.fabric.microsoft.com/75d21c50-d4ae-4778-98e3-41ec1f463ab5/Tables/oct_errors",
        "abfss://ce1d0a35-d7f8-462c-895f-da3fb1d7f85f@msit-onelake.dfs.fabric.microsoft.com/75d21c50-d4ae-4778-98e3-41ec1f463ab5/Tables/oct_shortcuts_stage",
        "abfss://ce1d0a35-d7f8-462c-895f-da3fb1d7f85f@msit-onelake.dfs.fabric.microsoft.com/75d21c50-d4ae-4778-98e3-41ec1f463ab5/Tables/oct_tables",
        "abfss://ce1d0a35-d7f8-462c-895f-da3fb1d7f85f@msit-onelake.dfs.fabric.microsoft.com/75d21c50-d4ae-4778-98e3-41ec1f463ab5/Tables/oct_shortcuts",
        "abfss://ce1d0a35-d7f8-462c-895f-da3fb1d7f85f@msit-onelake.dfs.fabric.microsoft.com/75d21c50-d4ae-4778-98e3-41ec1f463ab5/Tables/oct_expression",
        "abfss://ce1d0a35-d7f8-462c-895f-da3fb1d7f85f@msit-onelake.dfs.fabric.microsoft.com/75d21c50-d4ae-4778-98e3-41ec1f463ab5/Tables/oct_measures",
        "abfss://ce1d0a35-d7f8-462c-895f-da3fb1d7f85f@msit-onelake.dfs.fabric.microsoft.com/75d21c50-d4ae-4778-98e3-41ec1f463ab5/Tables/oct_model_v1",
        "abfss://ce1d0a35-d7f8-462c-895f-da3fb1d7f85f@msit-onelake.dfs.fabric.microsoft.com/75d21c50-d4ae-4778-98e3-41ec1f463ab5/Tables/oct_parameters",
        "abfss://ce1d0a35-d7f8-462c-895f-da3fb1d7f85f@msit-onelake.dfs.fabric.microsoft.com/75d21c50-d4ae-4778-98e3-41ec1f463ab5/Tables/oct_relationships",
        "abfss://ce1d0a35-d7f8-462c-895f-da3fb1d7f85f@msit-onelake.dfs.fabric.microsoft.com/75d21c50-d4ae-4778-98e3-41ec1f463ab5/Tables/oct_roles_v1",
        "abfss://ce1d0a35-d7f8-462c-895f-da3fb1d7f85f@msit-onelake.dfs.fabric.microsoft.com/75d21c50-d4ae-4778-98e3-41ec1f463ab5/Tables/workspacelist",
        "abfss://ce1d0a35-d7f8-462c-895f-da3fb1d7f85f@msit-onelake.dfs.fabric.microsoft.com/75d21c50-d4ae-4778-98e3-41ec1f463ab5/Tables/workspacelistv1",
        "abfss://ce1d0a35-d7f8-462c-895f-da3fb1d7f85f@msit-onelake.dfs.fabric.microsoft.com/75d21c50-d4ae-4778-98e3-41ec1f463ab5/Tables/datasetlist",
        "abfss://ce1d0a35-d7f8-462c-895f-da3fb1d7f85f@msit-onelake.dfs.fabric.microsoft.com/75d21c50-d4ae-4778-98e3-41ec1f463ab5/Tables/ds_published_status",
        "abfss://ce1d0a35-d7f8-462c-895f-da3fb1d7f85f@msit-onelake.dfs.fabric.microsoft.com/75d21c50-d4ae-4778-98e3-41ec1f463ab5/Tables/oct_measuresbridge",
        "abfss://ce1d0a35-d7f8-462c-895f-da3fb1d7f85f@msit-onelake.dfs.fabric.microsoft.com/75d21c50-d4ae-4778-98e3-41ec1f463ab5/Tables/oct_tables_without_relationship",
        "abfss://ce1d0a35-d7f8-462c-895f-da3fb1d7f85f@msit-onelake.dfs.fabric.microsoft.com/75d21c50-d4ae-4778-98e3-41ec1f463ab5/Tables/oct_roles_v1_final",
        "abfss://ce1d0a35-d7f8-462c-895f-da3fb1d7f85f@msit-onelake.dfs.fabric.microsoft.com/75d21c50-d4ae-4778-98e3-41ec1f463ab5/Tables/msxitelemetry_details",
        "abfss://ce1d0a35-d7f8-462c-895f-da3fb1d7f85f@msit-onelake.dfs.fabric.microsoft.com/75d21c50-d4ae-4778-98e3-41ec1f463ab5/Tables/oct_columnv1",
        "abfss://ce1d0a35-d7f8-462c-895f-da3fb1d7f85f@msit-onelake.dfs.fabric.microsoft.com/75d21c50-d4ae-4778-98e3-41ec1f463ab5/Tables/oct_tablesrls_check",
        "abfss://ce1d0a35-d7f8-462c-895f-da3fb1d7f85f@msit-onelake.dfs.fabric.microsoft.com/75d21c50-d4ae-4778-98e3-41ec1f463ab5/Tables/oct_graph_relationships",
        "abfss://ce1d0a35-d7f8-462c-895f-da3fb1d7f85f@msit-onelake.dfs.fabric.microsoft.com/75d21c50-d4ae-4778-98e3-41ec1f463ab5/Tables/oct_graph_relationships_bridge"
        ]
    def optimize_table(path):
        try:
            delta_table = DeltaTable.forPath(spark, path)
            delta_table.optimize().executeCompaction()
            #print(f"Optimized: {path}")
            spark.sql("refresh table datasetlistv1")
            spark.sql("refresh table factoct")
            spark.sql("refresh table lakehouselist")
            spark.sql("refresh table lakehouselistv1")
            spark.sql("refresh table oct_column")
            spark.sql("refresh table oct_errors")
            spark.sql("refresh table oct_shortcuts_stage")
            spark.sql("refresh table oct_tables")
            spark.sql("refresh table oct_expression")
            spark.sql("refresh table oct_measures")
            spark.sql("refresh table oct_model_v1")
            spark.sql("refresh table oct_parameters")
            spark.sql("refresh table oct_relationships")
            spark.sql("refresh table oct_roles_v1")
            spark.sql("refresh table oct_shortcuts")
            spark.sql("refresh table workspacelist")
            spark.sql("refresh table workspacelistv1")
            spark.sql("refresh table datasetlist")
            spark.sql("refresh table ds_published_status")
            spark.sql("refresh table oct_measuresbridge")
            spark.sql("refresh table oct_tables_without_relationship")
            spark.sql("refresh table oct_roles_v1_final")
            spark.sql("refresh table msxitelemetry_details")
            spark.sql("refresh table oct_columnv1")
            spark.sql("refresh table oct_tablesrls_check")
            spark.sql("refresh table oct_graph_relationships")
            spark.sql("refresh table oct_graph_relationships_bridge")
        except Exception as e:
            print(f"Error optimizing 3 {path}: {e}")

    with ThreadPoolExecutor(max_workers=27) as executor:  
        executor.map(optimize_table, table_paths)
    return "Operation Completed"


# In[65]:


def run_parallel_tasks():
    with ThreadPoolExecutor(max_workers=9) as executor:
        futures = [
            executor.submit(create_workspacelistv1_table),
            executor.submit(create_datasetlistv1_table),
            executor.submit(create_lakehouselistv1_table),
            executor.submit(create_modetype_temp_view),
            executor.submit(save_factocttable),
            executor.submit(oct_measuresbridge),
            executor.submit(save_measures),
            executor.submit(save_oct_roles_final),
            executor.submit(save_tables_without_relationship)
        ]
        # Optionally wait for all futures to complete and collect results or handle exceptions
        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"Error in task 4: {e}")


# In[66]:


def upsert_dataset_lineage(results,DatasetID):
    error_schema = StructType([
                    StructField("Workspace_ID", StringType(), True),
                    StructField("Item_Type", StringType(), True),
                    StructField("Item_ID", StringType(), True),
                    StructField("Error_Message", StringType(), True),
                    StructField("Alias", StringType(), True),
                    StructField("ModifiedTime", TimestampType(), True)
                ])
    errors = spark.createDataFrame([],error_schema)
    spark_model = results[0][0]
    model_errors = results[0][1]
    spark_relationships = results[1][0]
    relationship_errors = results[1][1]
    spark_roles = results[2][0]
    roles_errors = results[2][1]
    spark_tables = results[3][0]
    tables_errors = results[3][1]
    spark_columns= results[4][0]
    columns_errors = results[4][1]
    spark_measures = results[5][0]
    measures_errors = results[5][1]
    spark_expressions = results[6][0]
    expressions_errors = results[6][1]
    errors = errors.unionByName(model_errors)
    errors = errors.unionByName(relationship_errors)
    errors = errors.unionByName(roles_errors)
    errors = errors.unionByName(tables_errors)
    errors = errors.unionByName(columns_errors)
    errors = errors.unionByName(measures_errors)
    errors = errors.unionByName(expressions_errors)
    if not(spark_model.isEmpty()):
        spark_model= spark_model.dropDuplicates()
    if not(spark_relationships.isEmpty()):
        spark_relationships = spark_relationships.dropDuplicates()
    if not(spark_roles.isEmpty()):  
        spark_roles = spark_roles.dropDuplicates()  
    if not(spark_tables.isEmpty()):
        spark_tables = spark_tables.dropDuplicates()
    if not(spark_columns.isEmpty()):  
        spark_columns = spark_columns.dropDuplicates()  
    if not(spark_measures.isEmpty()):
        spark_measures = spark_measures.dropDuplicates()
    if not(spark_expressions.isEmpty()):  
        spark_expressions = spark_expressions.dropDuplicates()  
    if not(errors.isEmpty()):
        errors = errors.dropDuplicates()
       
    spark.sql(f"DELETE FROM oct_model_v1 WHERE DatasetID = '{DatasetID}'")
    spark.sql(f"DELETE FROM oct_relationships WHERE DatasetID = '{DatasetID}'")
    spark.sql(f"DELETE FROM oct_roles_v1 WHERE DatasetID = '{DatasetID}'")
    spark.sql(f"DELETE FROM oct_tables WHERE Dataset_ID = '{DatasetID}'")
    spark.sql(f"DELETE FROM oct_column WHERE Dataset_ID = '{DatasetID}'")
    spark.sql(f"DELETE FROM oct_measures WHERE Dataset_ID = '{DatasetID}'")
    spark.sql(f"DELETE FROM oct_expression WHERE Dataset_ID = '{DatasetID}'")
    spark.sql(f"DELETE FROM oct_errors WHERE Item_ID = '{DatasetID}'")
    spark_model.write.format("delta").mode("append").saveAsTable("oct_model_v1")
    spark_relationships.write.format("delta").mode("append").saveAsTable("oct_relationships")
    spark_roles.write.format("delta").mode("append").saveAsTable("oct_roles_v1")
    spark_tables.write.format("delta").mode("append").saveAsTable("oct_tables")
    spark_columns.write.format("delta").mode("append").saveAsTable("oct_column")
    spark_measures.write.format("delta").mode("append").saveAsTable("oct_measures")
    spark_expressions.write.format("delta").mode("append").saveAsTable("oct_expression")
    errors.write.format("delta").mode("append").saveAsTable("oct_errors")
    
    return "Operation Completed"


# In[67]:


def encapsulate_dataset(WorkspaceID,DatasetID):
    results = get_dataset_lineage(WorkspaceID,DatasetID)
    upsert_msg = upsert_dataset_lineage(results,DatasetID)
    return results


# In[68]:


def encapsulate_parameters(WorkspaceID,DatasetID,LakehouseWorkspaceID,LakehouseID,Alias,ModifiedTime):
    spark.sql(f"Delete from workspacelist where ID in ('{LakehouseWorkspaceID}','{WorkspaceID}')")
    spark.sql(f"Delete from datasetlist where ID in ('{DatasetID}')")
    spark.sql(f"Delete from lakehouselist where ID in ('{LakehouseID}')")
    datasetname = get_dataset_name(WorkspaceID, DatasetID)
    lakehousename= get_lakehouse_name(LakehouseWorkspaceID,LakehouseID)
    datasetworkspacename= get_workspace_name(WorkspaceID)
    lakehouseworkspacename = get_workspace_name(LakehouseWorkspaceID)
    
    datasetname.write.format("delta").mode("append").saveAsTable("datasetlist")
    lakehousename.write.format("delta").mode("append").saveAsTable("lakehouselist")
    if LakehouseWorkspaceID == WorkspaceID:
        datasetworkspacename.write.format("delta").mode("append").saveAsTable("workspacelist")
    else:
        datasetworkspacename.write.format("delta").mode("append").saveAsTable("workspacelist")
        lakehouseworkspacename.write.format("delta").mode("append").saveAsTable("workspacelist")

    spark.sql(f"DELETE FROM oct_parameters WHERE DatasetID = '{DatasetID}'")
    spark.sql(f"INSERT INTO oct_parameters VALUES ('{WorkspaceID}', '{DatasetID}', '{LakehouseWorkspaceID}','{LakehouseID}','{Alias}','{ModifiedTime}')")
    return "Operations Completed"


# In[69]:


def encapsulate_shortcuts(LakehouseWorkspaceID,LakehouseID):
   shortcuts,shortcuts_errors =  final_shortcuts(WorkspaceID = LakehouseWorkspaceID,LakehouseID = LakehouseID)


# In[70]:


def run_parallel_tasks_oct(WorkspaceID,DatasetID,LakehouseWorkspaceID,LakehouseID,Alias,ModifiedTime):
    encapsulate_parameters(WorkspaceID,DatasetID,LakehouseWorkspaceID,LakehouseID,Alias,ModifiedTime)
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(encapsulate_dataset,WorkspaceID,DatasetID),
            executor.submit(final_shortcuts,LakehouseWorkspaceID,LakehouseID)
        ]
        # Optionally wait for all futures to complete and collect results or handle exceptions
        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"Error in task: 5 {e}")
    return "Operation Completed"


# In[71]:


def run(WorkspaceID,DatasetID,LakehouseWorkspaceID = "NA",LakehouseID = "NA"):
    if LakehouseWorkspaceID == "NA" and LakehouseID == "NA":
        try:
            rootlocation = fabric.evaluate_dax(dataset= DatasetID,workspace = WorkspaceID,dax_string = """select [rootlocation] from $SYSTEM.TMSCHEMA_DELTA_TABLE_METADATA_STORAGES""")
            rootlocation = spark.createDataFrame(rootlocation)
            if rootlocation.isEmpty():
                pass
                print("Root Lakehouse Details Extraction Failed")
            else:
                rootlocation = rootlocation.withColumn('LakehouseWorkspaceID', regexp_extract('rootlocation', r'^/([^/]+)/([^/]+)/', 1)) \
                                .withColumn('LakehouseID', regexp_extract('rootlocation', r'^/([^/]+)/([^/]+)/', 2)) 
                rootlocation = rootlocation.select('LakehouseWorkspaceID', 'LakehouseID').dropDuplicates()
                rootlocation = rootlocation.filter(col("LakehouseID").isNotNull())  
                first_row = rootlocation.first()
                LakehouseWorkspaceID = first_row.LakehouseWorkspaceID
                LakehouseID = first_row.LakehouseID
        except Exception as e:
            print(f"Warning, we need lakehouse details to capture the shortcuts information.")
    Alias = get_executer_alias()
    ModifiedTime = get_modifiedtimestamp()
    run_parallel_tasks_oct(WorkspaceID,DatasetID,LakehouseWorkspaceID,LakehouseID,Alias,ModifiedTime)
    run_parallel_tasks()
    save_msxitelemetry_details()
    DS_Published_Status()
    save_oct_columnv1()
    oct_graph_relationships()
    oct_graph_relationships_bridge()
    save_oct_TablesRLS()
    final_optimize_tables()
    refreshmsg = refresh_dataset()
    return "Operation Completed"


# In[72]:


def run_pipeline():
    spark.sql("delete from oct_errors")
    Alias = get_executer_alias()
    ModifiedTime = get_modifiedtimestamp()
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(get_all_dataset_lineage),
            executor.submit(final_all_shortcuts)
        ]
    run_parallel_tasks()
    save_msxitelemetry_details()
    DS_Published_Status()
    save_oct_columnv1()
    oct_graph_relationships()
    oct_graph_relationships_bridge()
    save_oct_TablesRLS()
    final_optimize_tables()
    refresh_dataset()
    return "Operation Completed"

