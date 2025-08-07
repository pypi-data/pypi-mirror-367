from mtbs.mtbs import Mtbs
def main():

    # _mtbs = Mtbs(env="prd")
    # _db_list = _mtbs.databases_list()
    # # print(_mtbs.send_sql(query="SELECT * FROM uploaded_file limit 1", database=_db_list['Uploads API'], raw=False, cache_enabled=True))
    # print(_mtbs.send_sql(query="SELECT * FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';", database=_db_list['Uploads API'], raw=False, cache_enabled=True))

    
    #_mtbs.send_sql(query="SELECT * FROM my_table", database="my_database", raw=True, cache_enabled=True)

    fffff = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    subscription_get_documents = f"""
    SELECT pi.project_id, btrim(id_txt)::uuid AS file_id, p.company_id, p.siren
    FROM provided_info pi
    JOIN project p ON p.id = pi.project_id
    CROSS JOIN LATERAL json_array_elements_text(pi.value::json) AS arr(id_txt)
    WHERE (p.company_id is not null or p.siren is not null) and pi.data_type = 'FILE'
    AND pi.value IS NOT NULL
    AND jsonb_typeof(pi.value::jsonb) = 'array'
    AND btrim(id_txt) ~* '{fffff}'
    AND product_slug in ('assurance-caution-export', 'assurance-prospection',
    'exporter-prefi-agreement-request', 'partner-prefi-agreement-request', 'gpae')
    """

    mtbs = Mtbs(env='prd')
    dbs = mtbs.databases_list()
    print("Available databases:", dbs)
    
    # Exemple d'utilisation
    query = subscription_get_documents
    database_id = dbs['Subscription API']
    
    # Exporter en JSON
    result_json = mtbs.export_query_result(query, database_id, format_type="json")
    print("JSON Result:", result_json)
    
    # # Exporter en CSV
    # csv_file = mtbs.export_query_result(query, database_id, format_type="csv", output_file="output.csv")
    # print("CSV exported to:", csv_file)
    
    # # Exporter en DataFrame
    # df = mtbs.export_to_dataframe(query, database_id)
    # print("DataFrame shape:", df.shape)