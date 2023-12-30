import re

# 定义一个字典以跟踪每个URL的重试次数。
retry_counts = {}
# 设置每个URL的最大重试次数。
max_retries = 50

# 页面关键词 1
#本质是验证码页面                       
PAGE_ENTER_CHARACTERS = 'Enter the characters you see below' 

# 页面关键词 2
#本质是404页面
PAGE_SORRY_NOT_FIND = "Sorry! We couldn't find that page" 
PAGE_SORRY_NOT_FUNCTIONING = "We're sorry. The Web address you entered is not a functioning page on our site"
#本质是报错页面
PAGE_SORRY_SOMETHING_WRONG =  "Sorry! Something went wrong" 

 

path_pattern = re.compile(r'(GET|POST)\s+([^ ]+)\s+HTTP')


def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=50,
                           requestsPerConnection=100,
                           pipeline=False
                           )

    for word in open('C://Users/liqiye/Desktop/amazon/xss/aaa.txt'):
        engine.queue(target.req, word.rstrip())


def handleResponse(req, interesting):
    # 目前可用的属性包括 req.status(请求状态码)、req.wordcount(词数)、req.length(长度)和req.response(响应)
    # 条件检查
    retrie_check = (
        req.status == 503 or
        req.status == 505 or
        req.status == 429 or
        PAGE_ENTER_CHARACTERS in req.response or
        req.length == 17676 or
        req.length == 17677 or
        req.length == 17536
    )

    add_table_check = (
        req.status != 404 and
        req.status != 301 and
        req.status != 302 and
        PAGE_SORRY_NOT_FIND not in req.response and
        PAGE_SORRY_NOT_FUNCTIONING not in req.response and
        PAGE_SORRY_SOMETHING_WRONG not in req.response
    )
    
    # 获取路径
    http_request = req.getRequest()
    match = path_pattern.search(http_request)
    path = match.group(2)

     # 记录到日志
    output_file = open("C://Users/liqiye/Desktop/amazon/log.txt","a+")
    RetryCounts = 'Retry:' + str(retry_counts.get(path, 0))
    output_file.write('{:<10} {:<50} {:<10} {:<15}\n'.format(str(req.status), path, str(req.length), RetryCounts))

    output_file.close()
    #debug 
    print path
    print retry_counts.get(path, 0)
    
    if retrie_check:
        retry_counts[path] = retry_counts.get(path, 0) + 1

        if retry_counts[path] <= max_retries:
            req.engine.queue(req.template, req.words[0])
        else:
            callbacks.addToSiteMap(req.getBurpRequest())
    elif add_table_check:
        table.add(req)
