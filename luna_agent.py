import json, os, re
from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference.models import SystemMessage, UserMessage
load_dotenv()

class LunaAgent:
    def __init__(self):
        self.endpoint=os.getenv('CIS_LLM_ENDPOINT','').strip()
        self.key=os.getenv('CIS_LLM_API_KEY','').strip()
        self.model=os.getenv('CIS_LLM_MODEL','hack-fest-gpt-5.6-luna').strip()
        if not self.endpoint or not self.key:
            raise RuntimeError('CIS_LLM_ENDPOINT and CIS_LLM_API_KEY must be configured in .env')
        self.client=ChatCompletionsClient(endpoint=self.endpoint,credential=AzureKeyCredential(self.key),api_version='2025-03-01-preview')

    @staticmethod
    def _json(raw):
        raw=str(raw or '').strip()
        try: return json.loads(raw)
        except Exception: pass
        raw=re.sub(r'^```(?:json)?\s*|\s*```$','',raw,flags=re.I|re.S).strip()
        try: return json.loads(raw)
        except Exception:
            a=raw.find('{'); b=raw.rfind('}')
            if a>=0 and b>a: return json.loads(raw[a:b+1])
        raise ValueError('Luna returned non-JSON output: '+raw[:1200])

    def ask(self, system, payload, temperature=None):
        content=json.dumps(payload,ensure_ascii=False,default=str)
        messages=[SystemMessage(content=system),UserMessage(content=content)]
        kwargs={'messages':messages,'model':self.model,'headers':{'Authorization':self.key}}
        if temperature is not None: kwargs['temperature']=temperature
        res=self.client.complete(**kwargs)
        return self._json(res.choices[0].message.content)

    def select_product(self, row, candidates):
        system='''You are the Product Truth Agent product-identification specialist. Select only a candidate URL supplied in the evidence. Never invent a URL. Match the exact product/variant using barcode, brand, product description, size and other supplied evidence. If no candidate is sufficiently supported, return null URL and explain why.'''
        payload={'task':'select_exact_product','input_product':row,'candidates':[{'title':c.get('title'),'url':c.get('url'),'snippet':c.get('snippet'),'score':c.get('score'),'page_title':c.get('page',{}).get('title'),'page_text':c.get('page',{}).get('text','')[:12000]} for c in candidates]}
        return self.ask(system,payload)

    def classify_module(self,row,modules,candidates):
        system='''You are a taxonomy classifier. Choose exactly one MODULE from the supplied module list. Use only product evidence and the dataset module names. Do not invent a module. Return JSON only: {"module":"...","confidence":"high|medium|low","reasoning":"..."}.'''
        payload={'input_product':row,'allowed_modules':modules,'product_evidence':[{'url':c.get('url'),'title':c.get('title'),'snippet':c.get('snippet'),'page_text':c.get('page',{}).get('text','')[:10000]} for c in candidates[:4]]}
        return self.ask(system,payload)

    def classify_characteristics(self,row,context,evidence,product_url):
        system='''You are Product Truth Agent. Use ONLY supplied product evidence, taxonomy and guidelines. For every characteristic defined for the module, select a value. Closed characteristics MUST use an exact value from possible_values. Open characteristics may use an evidence-supported value. Apply defaults in the guidelines when evidence is absent. Do not invent product facts. Return JSON only with this exact shape: {"characteristics":{},"reasoning":"...","evidence":[{"claim":"...","source_url":"...","support":"supported|not_supported|unclear"}]}.'''
        payload={'input_product':row,'module_context':context,'product_url':product_url,'evidence':evidence}
        return self.ask(system,payload)
