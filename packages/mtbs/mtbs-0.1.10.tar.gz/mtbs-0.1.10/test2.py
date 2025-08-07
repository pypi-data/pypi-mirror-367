

import json
import requests
from mtbs import payload_template_v2
from mtbs.mtbs import read_metabase_config_from_browser

VALUE_REGEX = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
subscription_get_documents = {
    "query": f"SELECT pi.project_id, btrim(id_txt)::uuid AS file_id, p.company_id, p.siren FROM provided_info pi JOIN project p ON p.id = pi.project_id CROSS JOIN LATERAL json_array_elements_text(pi.value::json) AS arr(id_txt) WHERE (p.company_id is not null or p.siren is not null) and pi.data_type = 'FILE' AND pi.value IS NOT NULL AND jsonb_typeof(pi.value::jsonb) = 'array' AND btrim(id_txt) ~* '{VALUE_REGEX}' AND product_slug in ('assurance-caution-export', 'assurance-prospection', 'exporter-prefi-agreement-request', 'partner-prefi-agreement-request', 'gpae') and pi.project_id = 144948""".strip()}

def m1():

    url = 'https://metabase-prd.prod.bel.cloud.bpifrance.fr/api/dataset/json'

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Referer': 'https://metabase-prd.prod.bel.cloud.bpifrance.fr/question',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Origin': 'https://metabase-prd.prod.bel.cloud.bpifrance.fr',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Priority': 'u=0',
    }

    cookies = {
        'metabase.DEVICE': '8afdfb9d-3125-42f6-a45d-acc40edfe19a',
        'metabase.TIMEOUT': 'alive',
        'metabase.SESSION': 'b4f2104a-0062-4b8f-bc4b-aa8187eb0a44',
        'TS01870877': '01450ecb5790a445b8fd361217877f88debb52d05ac93fbdc14fdcbc97ba33e11d7c0843d52fcd7ba98e0e08d022b25b4bd39f4688',
        'PROD-PD-S-SESSION-ID': '1_9PFRp3aqIMcz9dnSDbO7FkZgDY+SBBU/O7QF61+e4R4RAGWNSAo=_AAAAAgA=_upGsQiYyjf2Rc2jixiihvmFYhAw=',
        '_oauth2_proxy_prd': 'FVm7mcB-5ZpG7_DZinjhbQ9VNRh1BXhW0xBZ5xJP3e-RjFqUo25XZvOX2v_mXJEtkfXxx-w6ZbCRn97jFJmdvOMEDryDkT_zGJOUqgpVnenAXBphnncOz1zkDld3a4FwVdNiOsTZcjOCyJ0l_K4iRFhDi652oiki9pbTRYfFn1YtKdwzzMc2aKVwzO2try0_xJEnVjB4yWcQe055MHX24ic4EBXMulGf77N6hB_tT_FgjL5HbSiytKVpVC-kY1bBvjGZftfPJQvPVZ_OKqIZvxNCn4qJ81q2bl6vO8MncuGosnmOUo7khpYPZshGONcBHh4KHBVuhFwEGamjilfG-3natO4I0VPdEiBsclsrjLZ6x4sfzbdpKeZZwJMAM7vYNhL1YuRKZgOehSw9WZgNVxlJZZRo7LkV6cj9VSndYNcxunG1KrpE0ryeVSPxrzFNuKNVdntWaXKPD3vdJyJ5mzJsWP0_eeajjMuDMaXacIPQg-Sn30zkyVGhcP_w0osbkMd7B6Y5jGR4dlvjokaFZ2kvgQjveEpvNGA4W3ComctqQs4fqEMNp4DUjGUnSEU9xRgyVRkh01k-ovT98dqWaP8VuSstXNDWQVQwh9NfdCHUgE0p0WKy-P2nk008GEXfFmm0GeIOWU-dhEwspcgiZ5VmfHUyd23XU2NPwKUrEpCv0brikQ_CaZUKmNFLHVkc8w7rqYGKw-HX5NKAH-573XS7Q-hNN2eUGEyjuukEF-1K9aY0dWq9Mib5SBzOgKD2KuPrKD_4xGh-w4oqvoRdW96_dx6znq1WJH_T2PbV-zjNMcyfJk5IyylacB_XPWh3fK1B08P8otQpjD4eHLEnymH985dVI7C1ZfNc0bK2dMhwTozuiBSXvjM8xYmpyy00PCDfBse1Of8-RV7vrpoM77HAsLKrCaY09eU8eXP5_rtaAuQSn9-jIFKO0UtrQI1cMZo5Tc7g7XQ4tNhXB2r8jj45rTF_nKAoyuqOwY26csrNOgDyDNsJoIU0siZ6Z7GPBSEDCJJjmftM5BdgkXDWWGYMEMj94mHodq-dMFXDCfkxcz_lSZvl9A8YtWiNuH4NEUeI8pnU_SmRqq5G212pDifAMlSq31jFULwlcP9xiPXr1mUYd8OXak3zExltdLjYqnJgVUlm8GXW1rxYCFHiujnrQ2Cp4FNYVF6ffCaONVBIm4zf--GyUl48O-yhWMTXL4NKVIS44shbfVmD18KM4KMgn_ycktxMCpKUnj2dTswdXoSd7gRZF2BrZNotRwINbl4jIHrcTVCl9IPF3K_oIegcVT_7O2604aAK0gv3tkOB3nSj6TGK9RvLgdTfQ4ktKpppmHMkfr9BeAIa4uHqjHK5EbQcQr7r0p3g0Brh6s51XZD2YrueQBRLg9CxpOozbGJBTMvZpZdlL4utQKc8xDEo-7JDGxhDsB0PAyx3ZFKRRUhpURTn6kR4pg_TAyHzoLLl_XjGs4GUUTV6pvP-7jj3UY3_CGUM_ePljoEaXh6J_ePllzXxXfoVeDzPIACimkQ8hanUl_sAavUozLF0Jtei6cRiiX_bVO5lBySViU4MzMltI-vsMudXxlmMvZxWxwNih01C5atYmkwk9T62o8j0xuc4m0_rMOYmcd-D8HTcnoUnOMDDJAPajdnQN9y7ohjavnlmpfkG12GK'
    }
    print(f"m1: \n headers: {headers} \n url: {url} \n cookies: {cookies}")
    data = {
        'query': '{"type":"native","native":{"query":" SELECT pi.project_id, btrim(id_txt)::uuid AS file_id, p.company_id, p.siren\n FROM provided_info pi\n JOIN project p ON p.id = pi.project_id\n CROSS JOIN LATERAL json_array_elements_text(pi.value::json) AS arr(id_txt)\n WHERE (p.company_id is not null or p.siren is not null) and pi.data_type = \'FILE\'\n AND pi.value IS NOT NULL\n AND jsonb_typeof(pi.value::jsonb) = \'array\'\n AND btrim(id_txt) ~* \'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$\'\n AND product_slug in (\'assurance-caution-export\', \'assurance-prospection\',\n \'exporter-prefi-agreement-request\', \'partner-prefi-agreement-request\', \'gpae\')\n and pi.project_id = 144948 limit 1;","template-tags":{}},"database":5,"middleware":{"js-int-to-string?":true,"add-default-userland-constraints?":true}}',
        'visualization_settings': '{"column_settings":{},"table.pivot":false,"table.pivot_column":"project_id","table.cell_column":"siren","table.columns":[{"name":"project_id","fieldRef":["field","project_id",{"base-type":"type/BigInteger"}],"enabled":true},{"name":"file_id","fieldRef":["field","file_id",{"base-type":"type/UUID"}],"enabled":true},{"name":"company_id","fieldRef":["field","company_id",{"base-type":"type/Text"}],"enabled":true},{"name":"siren","fieldRef":["field","siren",{"base-type":"type/Text"}],"enabled":true}],"table.column_formatting":[]}'
    }
    
    response = requests.post(url, headers=headers, cookies=cookies, data=data)

    print(response.status_code)
    print(response.text)

def m2():
    mtbs_base_url, mtbs_db_list_url, _headers, _headers_data = read_metabase_config_from_browser('prd')
    #print(mtbs_base_url, mtbs_db_list_url, _headers, _headers_data)
    p = payload_template_v2(query=subscription_get_documents['query'], database=5)
    {'query': json.dumps(p), 'visualization_settings': f"'{visualization_settings}'"}
    visualization_settings = {
        "column_settings":{},
        "table.pivot":False,
        "table.pivot_column":"project_id",
        "table.cell_column":"siren","table.columns":[{"name":"project_id","fieldRef":["field","project_id",{"base-type":"type/BigInteger"}],"enabled":True},{"name":"file_id","fieldRef":["field","file_id",{"base-type":"type/UUID"}],"enabled":True},{"name":"company_id","fieldRef":["field","company_id",{"base-type":"type/Text"}],"enabled":True},{"name":"siren","fieldRef":["field","siren",{"base-type":"type/Text"}],"enabled":True}],"table.column_formatting":[]}
    
    url = f'{mtbs_base_url}/json'

    print(f"m1: \n headers: {headers} \n url: {url} \n cookies: {cookies}")
    response = requests.post(url, headers=_headers, cookies=cookies, data=data)

if __name__ == "__main__":
    m1()
    m2()