import re

#魔术字符串
#%s&rjawmVk=z456

#定义一个字典以跟踪每个URL的重试次数。
retry_counts = {}
#设置每个URL的最大重试次数。
max_retries = 200

#页面关键词
#本质是验证码页面                       
PAGE_ENTER_CHARACTERS = 'Enter the characters you see below' 

#path_pattern = re.compile(r'(GET|POST)\s+([^ ]+)\s+HTTP')
path_pattern = re.compile(r'(GET|POST)\s+([^?]+)')

def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=50,
                           requestsPerConnection=100,
                           pipeline=False
                           )

    for word in open('C://Users/liqiye/Desktop/amazon/xss/burp.log'):
        engine.queue(target.req, word.rstrip())


def handleResponse(req, interesting):
    #目前可用的属性包括 req.status(请求状态码)、req.wordcount(词数)、req.length(长度)和req.response(响应)
    #条件检查
    count_z123 = req.response.count("z123")
    count_z456 = req.response.count("z456")

    is_z123_present = 'z123' in req.response
    is_condition_met = count_z456 == 0 or count_z123 > count_z456*50
        
    retrie_check = (
        req.status == 503 or
        req.status == 505 or
        req.status == 429 or
        PAGE_ENTER_CHARACTERS in req.response or
        req.length == 17676 or
        req.length == 17677 or
        req.length == 17536
    )
    
    #获取路径
    http_request = req.getRequest()
    match = path_pattern.search(http_request)
    path = match.group(2)
    
    #记录到日志
    output_file = open("C://Users/liqiye/Desktop/amazon/log.txt","a+")
    RetryCounts = 'Retry:' + str(retry_counts.get(path, 0))
    output_file.write('{:<10} {:<50} {:<10} {:<15}\n'.format(str(req.status), path, str(req.length), RetryCounts))

    output_file.close()
    #debug 
    print path
    print retry_counts.get(path, 0)

    #记录400请求
    if req.status == 400:
        callbacks.addToSiteMap(req.getBurpRequest())
    
    if retrie_check:
        retry_counts[path] = retry_counts.get(path, 0) + 1

        if retry_counts[path] <= max_retries:
            req.engine.queue(req.template, req.words[0])
        else:
            callbacks.addToSiteMap(req.getBurpRequest())
    elif is_z123_present and is_condition_met :
   
        req.label = 'z123:' + str(count_z456*50) + '~' + str(count_z123) + '|'
        
        lable_check = 0
            
        if "z'z" in req.response:
            req.label += "z'z:" + str(req.response.count("z'z")) + '|'
            lable_check = 1
        if 'z"z' in req.response:
            req.label += 'z"z:' + str(req.response.count('z"z')) + '|'
            lable_check = 1
        if 'z<z' in req.response:
            req.label += "z<z:" + str(req.response.count('z<z')) + '|'
            lable_check = 1

        # 其他标签 
        #<div id='rhf-context'> 防止过多误报
        if "<div id='rhf-context'>" in req.response:
            req.label += "        False Positive:<div id='rhf-context'>|"
         
        if lable_check:
            table.add(req)
