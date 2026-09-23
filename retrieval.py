import os, re, json, requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urlparse
from rapidfuzz.fuzz import ratio
from dotenv import load_dotenv
load_dotenv()

HEADERS={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X) Product Truth Agent/1.0'}
TIMEOUT=int(os.getenv('REQUEST_TIMEOUT','15'))
MAX_PAGE_CHARS=int(os.getenv('MAX_PAGE_CHARS','18000'))
MAX_RESULTS=int(os.getenv('MAX_SEARCH_RESULTS','8'))

BAD_DOMAINS={'facebook.com','instagram.com','youtube.com','pinterest.com','tiktok.com'}

def clean(s): return re.sub(r'\s+',' ',str(s or '')).strip()

def tokens(s):
    return [x for x in re.findall(r'[a-z0-9]+', str(s or '').lower()) if len(x)>2]

def extract_page(url, max_chars=MAX_PAGE_CHARS):
    try:
        r=requests.get(url,headers=HEADERS,timeout=TIMEOUT,allow_redirects=True)
        r.raise_for_status()
        soup=BeautifulSoup(r.text,'html.parser')
        for x in soup(['script','style','noscript','svg']): x.decompose()
        title=clean(soup.title.get_text(' ',strip=True) if soup.title else '')
        meta=' '.join(clean(x.get('content')) for x in soup.find_all('meta') if x.get('content'))
        text=clean(soup.get_text(' ',strip=True))
        return {'url':r.url,'title':title,'text':(title+' '+meta+' '+text)[:max_chars],'status':r.status_code}
    except Exception as e:
        return {'url':url,'title':'','text':'','status':None,'error':str(e)}

def _ddg(query, limit):
    url='https://html.duckduckgo.com/html/?q='+quote_plus(query)
    r=requests.get(url,headers=HEADERS,timeout=TIMEOUT)
    soup=BeautifulSoup(r.text,'html.parser'); out=[]
    for a in soup.select('.result__a')[:limit]:
        href=a.get('href')
        if href: out.append({'title':clean(a.get_text(' ',strip=True)),'url':href,'snippet':''})
    return out

def _bing(query, limit):
    url='https://www.bing.com/search?q='+quote_plus(query)
    r=requests.get(url,headers=HEADERS,timeout=TIMEOUT)
    soup=BeautifulSoup(r.text,'html.parser'); out=[]
    for li in soup.select('li.b_algo')[:limit]:
        a=li.select_one('h2 a'); p=li.select_one('.b_caption p')
        if a and a.get('href'):
            out.append({'title':clean(a.get_text(' ',strip=True)),'url':a['href'],'snippet':clean(p.get_text(' ',strip=True) if p else '')})
    return out

def _tavily(query, limit):
    key=os.getenv('TAVILY_API_KEY','').strip()
    if not key: return []
    r=requests.post('https://api.tavily.com/search',json={'api_key':key,'query':query,'max_results':limit,'include_raw_content':False},timeout=TIMEOUT)
    r.raise_for_status(); data=r.json();
    return [{'title':x.get('title',''),'url':x.get('url',''),'snippet':x.get('content','')} for x in data.get('results',[])]

def search_web(query, limit=MAX_RESULTS):
    for fn in (_tavily,_ddg,_bing):
        try:
            res=fn(query,limit)
            if res: return res
        except Exception:
            continue
    return []

def product_queries(row):
    barcode=clean(row.get('EXTERNAL_CODE')); brand=clean(row.get('BRAND')); desc=clean(row.get('RETAILER_DESC')); country=clean(row.get('COUNTRY'))
    qs=[]
    if barcode: qs += [f'"{barcode}"', f'"{barcode}" "{brand}"']
    if brand and desc: qs.append(f'"{brand}" {desc[:180]}')
    if desc: qs.append(f'"{desc[:180]}" {country}')
    return list(dict.fromkeys(qs))

def candidate_score(row, candidate, page):
    barcode=clean(row.get('EXTERNAL_CODE')).lower().replace("'",'')
    brand=clean(row.get('BRAND')).lower()
    desc=clean(row.get('RETAILER_DESC')).lower()
    blob=(candidate.get('title','')+' '+candidate.get('snippet','')+' '+page.get('title','')+' '+page.get('text','')).lower()
    score=0.0
    if barcode and barcode in blob: score += .55
    if brand and brand.split('(')[0].strip() and brand.split('(')[0].strip() in blob: score += .15
    target_tokens=set(tokens(desc)); hit=len(target_tokens & set(tokens(blob)))
    if target_tokens: score += min(.25, .25*hit/max(1,min(10,len(target_tokens))))
    score += .05*ratio(desc, blob[:2500])/100
    domain=urlparse(page.get('url') or candidate.get('url','')).netloc.lower().replace('www.','')
    if any(bad in domain for bad in BAD_DOMAINS): score -= .3
    return max(0,min(1,score))

def retrieve_product(row, max_results=MAX_RESULTS):
    candidates=[]; seen=set()
    for q in product_queries(row):
        for x in search_web(q,max_results):
            u=x.get('url','')
            if u and u not in seen:
                seen.add(u); candidates.append(x)
        if len(candidates)>=max_results: break
    scored=[]
    for c in candidates[:max_results]:
        page=extract_page(c['url'])
        scored.append({**c,'page':page,'score':round(candidate_score(row,c,page),4)})
    return sorted(scored,key=lambda x:x['score'],reverse=True)
