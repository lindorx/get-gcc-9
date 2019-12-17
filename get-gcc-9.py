import requests
import os
import hashlib
import re
import sys
import platform
import time

url ='http://ppa.launchpad.net/ubuntu-toolchain-r/test/ubuntu/pool/main/g/gcc-9/'


#下载函数
def downloader(url,filepath):
    start=time.time()
    size=0
    file=requests.get(url,stream=True)
    count=1024
    content_size=int(file.headers['content-length'])
    print('[  地址  ]:'+url)
    if file.status_code==200:
        if content_size<1024:       #字节 byte
            print('[文件大小]:%0.2f byte'%(content_size))
        elif content_size<1024*1024:     #Kb
            print('[文件大小]:%0.2f Kb'%(content_size/1024))
            count=2048
        else:       #Mb
            print('[文件大小]:%0.2f Mb'%(content_size/1024/1024))
            count=2048
        with open(filepath,'wb+')as f:
            for data in file.iter_content(chunk_size=count):
                f.write(data)
                size+=len(data)
                print('\r'+'[下载进度]:%s%0.2f%%'%('>'*int(size*50/content_size),float(size/content_size*100)),end='')
    end=time.time()
    print('[  耗时  ]：%0.2f'%(end-start))


if __name__=='__main__':
    #获取系统架构
    sysarch=platform.machine()
    sysarch=sysarch.lower()
    vermatch=r'href.*?cpp.*?\-doc_.*?ubuntu1~([\d|\.]*?)\_.*?.deb.*?'
    
    if url[len(url)-1]=='/':
        url=url[:-1]
    new_md5=hashlib.md5()
    new_md5.update(url.encode('utf8'))
    urlhash=str(new_md5.hexdigest())       #计算网址哈希值
    files=os.listdir('.')   #获取此目录文件名
    print('[获取网页]')
    fae=False
    for i in range(0,len(files)):
        if files[i][:-4]==urlhash:
            fae=True
            break
    if fae:#创建文件
        print('[网页已缓存，读取]')
        f=open(files[i],"r")
        strhtml=f.read()
        f.close()
    else:
        strhtml =requests.get(url)
        strhtml=strhtml.text
        #将网页写入文件
        f=open(urlhash+'.txt','w+')
        f.write(strhtml)
        f.close()
    print('[读取网页成功]')
    #读取支持的版本
    uvs=re.findall(vermatch,strhtml)
    if uvs==None:
        print('!获取版本信息错误，请检查正则表达式vermatch或'+urlhash+'.txt文件内的网页缓存')
        sys.exit()
    print('*'*50)
    for ver in uvs:
        print(ver)
    print('*'*50)
    vercheck=input('*上面是支持的Ubuntu版本，请输入对应的版本号：')
    isinarray=False
    for ver in uvs:
        if ver==vercheck:
            isinarray=True
            break
    if not isinarray:
        print('!输入版本不支持')
        sys.exit()
    
    archmatch=r'href.*?gcc.*?base.*?ubuntu1~'+vercheck+r'\_([\S]*?)\.deb'
    #读取支持的架构
    uas=re.findall(archmatch,strhtml)
    check=input('*本机系统架构为：'+sysarch+',手动选择?（n/y）:')
    if check!='':
        if check[0]=='y' or check=='Y':
            for arch in uas:
                print(arch)
            archeck=input('*上面是PPA中Ubuntu-'+vercheck+'支持的架构，输入对应架构：')
    else:
        archeck=sysarch
    isinarry=False
    for arch in uas:
        if arch==archeck:    
            isinarray=True
            break
    if not isinarray:
        print('架构不支持')
        sys.exit()

    filematch=r'href.*?"(.*?ubuntu1~'+vercheck+r'_'+archeck+r'\.deb)"'
    fname=re.findall(filematch,strhtml)#匹配文件名
    print('[完成文件名查找，开始写入文件]') 
    
    #将读取的文件名写入文件
    fnamelen=len(fname) #文件数量
    filename=urlhash+'_files.txt'
    f=open(filename,'w+')
    f.write('file num:'+str(fnamelen)+'\n')
    for line in fname:
        f.write(line+'\n')
    f.close()
    
    print('[文件名已写入文件]：'+filename)
    print('[共 '+str(fnamelen)+' 个文件]')
    
    #开始根据文件名下载文件
    check=input('*是否开始下载文件？（n/y）:')
    if check!='':
        if check[0]!='y' and check[0]!='Y':
            sys.exit()
    else:
        sys.exit()
    #创建文件夹
    dire=re.search(r'[^/]*$',url) #根据网址的匹配出文件夹名
    if dire==None:
        print('!文件夹名出错')
        sys.exit()
    dire=str(dire.group())
    
    print('[下载目录]:'+dire)
    isexists=os.path.exists(dire)
    if not isexists:
        os.mkdir(dire)
    dire=dire+'\\'
    
    for i in range(0,fnamelen):
        print('[开始下载]:'+fname[i])
        downloader(url+'/'+fname[i],fname[i])
        print('[下载完成]\n[剩余]:%d/%d'% (fnamelen-i-1,fnamelen))



