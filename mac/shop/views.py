from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import product, Contact, Order, OrderUpdate
from math import ceil
from django.contrib.auth import authenticate,login,logout
import json
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
#from PayTm import Checksum
from .models import product,productcomment
#from gateway.Checksum import generate_checksum
MERCHANT_KEY = 'kbzk1DSbJiV_O3p5'

def index(request):

    allProds = []
    catProds = product.objects.values('category', 'id')
    cats = {item['category'] for item in catProds}
    for cat in cats:
        prod = product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n//4 + ceil((n/4)-(n//4))
        allProds.append([prod, range(1, nSlides), nSlides])

    params = {'allProds': allProds}
    return render(request, 'shop/index.html', params)


def searchMatch(query, item):
    # return true only query matches the item
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True


def search(request):
    query = request.GET.get('search')
    allProds = []
    catProds = product.objects.values('category', 'id')
    cats = {item['category'] for item in catProds}
    for cat in cats:
        prodtemp = product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]

        n = len(prod)
        nSlides = n//4 + ceil((n/4)-(n//4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlides), nSlides])

    params = {'allProds': allProds, 'msg': ""}
    if len(allProds) == 0 or len(query) < 4:
        params = {'msg': "Please make sure to enter relevent search query"}
    return render(request, 'shop/search.html', params)


def about(request):
    return render(request, "shop/about.html")


def contact(request):
    thank = False
    if request.method == "POST":
        con_name = request.POST.get('name', '')
        con_email = request.POST.get('email', '')
        con_phone = request.POST.get('phone', '')
        con_desc = request.POST.get('desc', '')
        # print(name,email,phone,desc)
        mycontact = Contact(name=con_name, email=con_email,
                            phone=con_phone, desc=con_desc)
        mycontact.save()
        messages.success(request,"Your details successfully submited !" )
    return render(request, "shop/contact.html",)


def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('trackeremail','')
        print(orderId)
        print(email)
        try:
            order = Order.objects.filter(order_id=orderId, email=email)
            print(order)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status":"success", "updates": updates, "itemsJson": order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"Error"}')

    return render(request, 'shop/tracker.html')


def handleSignup(request):
    if request.method == 'POST':
        username = request.POST['uname']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        # check for errorneous input
        if len(username) >10:
            messages.error(request,"Username must be under 10 characters !")
            return redirect('/')

        if not username.isalnum():
            messages.error(request,"Username should only contains letters and numbers !")
            return redirect('/')
        
        if password1 != password2:
            messages.error(request,"Password do not match !")
            return redirect('/')


        # create the user

        myuser = User.objects.create_user(username, email, password1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.save()
        messages.success(request,f' {username}, Your account has been created !')
        return redirect('/shop/')

    else:
        return HttpResponse("404- Not Found")



def handleLogin(request):
    if request.method == 'POST':
        loginusername = request.POST['loginusername']
        loginpassword = request.POST['loginpassword']

        user=authenticate(username=loginusername,password=loginpassword)
        if user is not None:
            login(request,user)
            messages.success(request,f' Welcome {loginusername}, Your are successfully Logged In!')
            return redirect('/')
        else:
            messages.error(request,"Invalid credentials, Please try again !")
            return redirect('/')
       
    return HttpResponse('404- Not Found')


def handleLogout(request):
    logout(request)
    messages.success(request,"Your are successfully Logged Out !" )
    return redirect('/')

    


def productView(request, myid):
    # fetch the product using id
    products = product.objects.filter(id=myid)
    comments=productcomment.objects.filter(product=myid)
    poscount=0
    count=0
    for comment in comments:
        if comment.pos==1:
            poscount=poscount+1
        count=count+1        
    if count==0:
        pcount=0
        ncount=0
    else:        
        pcount=int((poscount*100)/count)
        print(poscount)
        print(count)
        ncount=100-pcount 
    return render(request, "shop/prodview.html", {'product': products[0],'id':myid,'comments':comments,'pcount':pcount,'ncount':ncount})


def checkout(request):
    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        amount = request.POST.get('amount', '')
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + \
            " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        pin_code = request.POST.get('pin_code', '')
        phone = request.POST.get('phone', '')
        # print(name,email,phone,desc)
        myorder = Order(items_json=items_json, name=name, email=email,
                        address=address, city=city, state=state, pin_code=pin_code, phone=phone, amount=amount)
        myorder.save()
        update = OrderUpdate(order_id=myorder.order_id,
                             update_desc="The order has been Placed")
        update.save()
        thank = True
        id = myorder.order_id
        messages.success(request,f'Thanks for ordering with us.Your order id is {id}. Use it to track your order using our order tracker' )
        #return render(request, 'shop/checkout.html',)
        #Request paytm to transfer the amount to your account after payment by user
        param_dict={
            'MID': 'pQZDMc54932484744157',
            'ORDER_ID':str(myorder.order_id),
            'TXN_AMOUNT':str(amount),
            'CUST_ID':email,
            'INDUSTRY_TYPE_ID':'Retail',
            'WEBSITE':'WEBSTAGING',
            'CHANNEL_ID':'WEB',
	        'CALLBACK_URL':'http://127.0.0.1:8000/shop/handlerequest/',
        }
        #param_dict['CHECKSUMHASH']=Checksum.generate_checksum(param_dict,)
        #return render(request,'shop/PayTm.html',{'param_dict':param_dict})

    return render(request, 'shop/checkout.html')

@csrf_exempt    
def handlerequest(request):
    #paytm will send you post request here
    form= request.POST
    response_dict={}
    for i in form.keys():
        response_dict[i]=form[i]
        if i== 'CHECKSUMHASH':
            checksum=form[i]
    
    verify=Checksum.verify_checksum(response_dict,MERCHANT_KEY,checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('Order Successful')
        else:
            print('Order was not Successful because'+ response_dict['RESPMSG'])
    return render(request, 'shop/paymentstatus.html',{'response': response_dict})



# def productcom(request):
#     if request.method=='POST':
#         comment=request.POST.get('comment')
#         user=request.user
#         productSno=request.POST.get('productSno')
#         prod=product.objects.get(id=productSno)

#         comment=productcomment(product=prod,user=user,comment=comment)
#         comment.save()
#         messages.success(request,"Thanks for your feedback:)")


        # return redirect(f'/shop/products/{prod.id}' )










def productcom(request):
    if request.method=='POST':
        comment=request.POST.get('comment')
        user=request.user

        productSno=request.POST.get('productSno')
        prod=product.objects.get(id=productSno)
         

        # parentSno=request.POST.get('parentSno')
        # if parentSno=="":
        # Model_Path='sentiment_model_lstm.h5'
        
        from sklearn.linear_model import LogisticRegression
        import pickle


        # load the vectorizer
        loaded_vectorizer = pickle.load(open('vectorizer.pickle', 'rb'))

        # load the model
        loaded_model = pickle.load(open('classification.model', 'rb'))


        #     # import pandas as pd
        #     # import nltk
        #     # import re
        # from keras.models import load_model
        #     # import numpy as np
        #     # from nltk.stem.porter import PorterStemmer
        #     # from nltk.corpus import stopwords
        #     #import tensorflow as tf
        #     # from tensorflow.keras.layers import Embedding
        # from tensorflow.keras.preprocessing.sequence import pad_sequences
        #     # from tensorflow.keras.models import Sequential
        # from tensorflow.keras.preprocessing.text import one_hot
        #     # from tensorflow.keras.layers import LSTM
        #     # from tensorflow.keras.layers import Dense
        #     #w = "good phones and best sound.Good for person who are not having time from office."
        #     ### Vocabulary size
        # voc_size = 5000
        # model = load_model(Model_Path)
        # onehot_rep = [one_hot(comment, voc_size)]

        # sent_length = 20
        # embed = pad_sequences(onehot_rep, padding='pre', maxlen=sent_length)
        # print(embed)
        # a=model.predict_classes(embed)
        # print(a)
        a=loaded_model.predict(loaded_vectorizer.transform([comment]).toarray())


            # comment=ShopComment(comment=comment,user=user)

        # comment = productcomment(product=prod,comment=comment, user=user)
        # comment.save()
        pos=0
        if a==[0]:
            messages.warning(request,f'Sorry for the inconvenience caused :( ')
        else:
            # if prod.positiveness==0:
            pos=1
            # prod.positiveness=1
            # else:
                # prod.positiveness=prod.positiveness+1    
            messages.success(request, f'Thanks for the positive feedback :)')
        # else:
        #     parent=ShopComment.objects.get(sno=parentSno)
        #     comment = ShopComment(product=prod,comment=comment, user=user,parent=parent)
        #     comment.save()
        #     messages.success(request, f'Your reply has been successfully created ... ')
        comment = productcomment(product=prod,comment=comment, user=user,pos=pos)
        comment.save()

        return redirect(f'/shop/products/{prod.id}' )
    else:
        return redirect('/shop/')
