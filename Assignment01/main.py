from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.oauth2.id_token;
from google.auth.transport import requests
from google.cloud import firestore
import starlette.status as status
from google.cloud.firestore_v1.base_query import FieldFilter
from fastapi import HTTPException

app = FastAPI()

firestore_db = firestore.Client()

firebase_request_adapter = requests.Request()

app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory="templates")

def getUser(user_token):
    user = firestore_db.collection('users').document(user_token['user_id'])
    if not user.get().exists:
        user_data = {
            'name': 'Jittu Jose',
            'ev_list': []  
        }
        
        firestore_db.collection('users').document(user_token['user_id']).set(user_data)
        
        

    return user

def getDataEV(constID):
    evdata = firestore_db.collection('evdata').document(constID)
    if not evdata.get().exists:
        ev_data = {
            'ev_list':[]
        }
        firestore_db.collection('evdata').document(constID).set(ev_data)
    return evdata

def validateFirebaseToken(id_token):
    if not id_token:
        return None
    
    user_token = None
    try:
        user_token = google.oauth2.id_token.verify_firebase_token(id_token,firebase_request_adapter)
    except ValueError as err:
        print(str(err))

    return user_token

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    id_token = request.cookies.get("token")
    error_message = "No error here"
    user_token = None
    user = None

    ev_data = getDataEV("jittu").get()
    evcars = []
    for evcar in ev_data.get('ev_list'):
        evcars.append(evcar.get())

    user_token = validateFirebaseToken(id_token)
    print(user_token)
    if not user_token:
        return templates.TemplateResponse('main.html',{'request': request,'user_token':None,'error_message': None, 'user_info':None, 'ev_list':evcars})
    
    
    user = getUser(user_token).get()
    
    
    return templates.TemplateResponse('main.html',{'request': request,'user_token': user_token,'error_message': error_message, 'user_info':user, 'ev_list':evcars})



# route that will take in an index for an address object to be deleted from firestore and the reference be removed from the user
@app.post("/delete-ev", response_class=RedirectResponse)
async def deleteAddress(request: Request):
# there should be a token. Validate it and if invalid then redirect back to / as a basic security measure
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token)
    if not user_token:
        return RedirectResponse('/')

# pull the index from our form
    form = await request. form()
    name = form['evname']
    


# pull the list of address objects from the user delete the requested index and update the user
    
    evcar = getDataEV("jittu")
    evcars = evcar.get().get('ev_list')

    #finding index in array to delete
    ev_data = getDataEV("jittu").get()
    evcararray = []
    index = -1
    for evcarone in ev_data.get('ev_list'):
        evcararray.append(evcarone.get())

    index=index = find_index_by_name(evcararray, name)
    

    evcars [int(index) ].delete()
    del evcars [int(index) ]
    data = {
        'ev_list': evcars
    }
    evcar. update(data)

    # when finished return a redirect with a 302 to force a get verb
    return RedirectResponse('/', status_code=status.HTTP_302_FOUND)



# Function to find the index of the object with the specified name
def find_index_by_name(array, name):
    for index, doc_snapshot in enumerate(array):
        # Extract the data from the DocumentSnapshot
        data = doc_snapshot.to_dict()
        # Check if the 'name' attribute matches
        if data.get('name') == name:
            return index
    # Return -1 if the name is not found in any object
    return -1

@app.get("/add-EV", response_class=HTMLResponse)
async def updateForm(request: Request):
    id_token = request.cookies.get("token")

    user_token = validateFirebaseToken(id_token)
    if not user_token:
        return RedirectResponse('/')
    
    user = getUser(user_token)
    return templates.TemplateResponse('addEV.html',{'request':request,'user_token': user_token,'error_message':None, 'user_info': user.get()})

@app.post("/add-EV", response_class=RedirectResponse)
async def updateFormPost(request:Request):
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token)
    if not user_token:
        return RedirectResponse('/')
    
    # pull the form containing our data
    form = await request.form()
    #checking the the new name is existing
    search = form['name']
    dummy_data_ref = firestore_db.collection('evdata')
    query = dummy_data_ref.where('name', '==', search).get()
    if query:
         return RedirectResponse('/', status_code=status.HTTP_302_FOUND)
# create a reference to an address object note that we have not given an ID here
# we are asking firestore to create an ID for us
    evcar_ref = firestore_db.collection('evdata').document()
    

# set the data on the address object
    evcar_ref. set({
        'name': form['name'],
        'manufact': form['manufact'],
        'year': int(form['year']),
        'battery': int(form['battery']),
        'wltp': int(form['wltp']),
        'cost': int(form['cost']),
        'power': int(form['power']),
        'review':[],
        'rating':[]
    })
# add ev details to firestore
    
    evcar = getDataEV("jittu")
    evcars = evcar.get().get('ev_list')
    evcars.append(evcar_ref)
    evcar.update({'ev_list': evcars})


    
# when finished return a redirect with a 302 to force a GET verb
    return RedirectResponse('/', status_code=status.HTTP_302_FOUND)

#Filter by name
@app.post("/filter-by-name", response_class=HTMLResponse)
async def filterByString(request: Request):
# there should be a token. Validate it and if invalid then redirect back to / as a basic security measure
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token)
    

    form = await request. form()
    search = form['nameEV']

    if not search:
        return RedirectResponse('/', status_code=status.HTTP_302_FOUND)


    dummy_data_ref = firestore_db.collection('evdata')
    query = dummy_data_ref.where(filter=FieldFilter('name','==',search))
    
    if not user_token:
        return templates.TemplateResponse('main.html',{'request': request,'user_token': user_token,'error_message': "no error", 'user_info':None, 'ev_list':query.stream()})

    user = getUser(user_token).get()
    return templates.TemplateResponse('main.html',{'request': request,'user_token': user_token,'error_message': "no error", 'user_info':user, 'ev_list':query.stream()})

#Filter by manufacturer
@app.post("/filter-by-manufact", response_class=HTMLResponse)
async def filterByManufact(request: Request):
# there should be a token. Validate it and if invalid then redirect back to / as a basic security measure
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token)
    

    form = await request. form()
    search = form['manufact']

    if not search:
        return RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    dummy_data_ref = firestore_db.collection('evdata')
    query = dummy_data_ref.where(filter=FieldFilter('manufact','==',search))
    
    if not user_token:
        return templates.TemplateResponse('main.html',{'request': request,'user_token': user_token,'error_message': "no error", 'user_info':None, 'ev_list':query.stream()})

    user = getUser(user_token).get()
    return templates.TemplateResponse('main.html',{'request': request,'user_token': user_token,'error_message': "no error", 'user_info':user, 'ev_list':query.stream()})

@app.post("/filter-by-battery", response_class=HTMLResponse)
async def filterByBattery(request: Request):
# there should be a token. Validate it and if invalid then redirect back to / as a basic security measure
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token)
    

    form = await request. form()
    low = form['lowb']
    high = form['highb']

    if not low or not high:
        return RedirectResponse('/', status_code=status.HTTP_302_FOUND)

    dummy_data_ref = firestore_db.collection('evdata')
    query = dummy_data_ref.where(filter=FieldFilter('battery','>=',int(low))).where(filter=FieldFilter('battery','<=',int(high)))
    
    if not user_token:
        return templates.TemplateResponse('main.html',{'request': request,'user_token': user_token,'error_message': "no error", 'user_info':None, 'ev_list':query.stream()})

    user = getUser(user_token).get()
    return templates.TemplateResponse('main.html',{'request': request,'user_token': user_token,'error_message': "no error", 'user_info':user, 'ev_list':query.stream()})

@app.post("/filter-by-wltp", response_class=HTMLResponse)
async def filterByWltp(request: Request):
# there should be a token. Validate it and if invalid then redirect back to / as a basic security measure
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token)
    

    form = await request. form()
    low = form['lowwltp']
    high = form['highwltp']
    if not low or not high:
        return RedirectResponse('/', status_code=status.HTTP_302_FOUND)


    dummy_data_ref = firestore_db.collection('evdata')
    query = dummy_data_ref.where(filter=FieldFilter('wltp','>=',int(low))).where(filter=FieldFilter('wltp','<=',int(high)))
    
    if not user_token:
        return templates.TemplateResponse('main.html',{'request': request,'user_token': user_token,'error_message': "no error", 'user_info':None, 'ev_list':query.stream()})

    user = getUser(user_token).get()
    return templates.TemplateResponse('main.html',{'request': request,'user_token': user_token,'error_message': "no error", 'user_info':user, 'ev_list':query.stream()})

@app.post("/filter-by-cost", response_class=HTMLResponse)
async def filterByCost(request: Request):
# there should be a token. Validate it and if invalid then redirect back to / as a basic security measure
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token)
    

    form = await request. form()
    low = form['lowcost']
    high = form['highcost']
    if not low or not high:
        return RedirectResponse('/', status_code=status.HTTP_302_FOUND)


    dummy_data_ref = firestore_db.collection('evdata')
    query = dummy_data_ref.where(filter=FieldFilter('cost','>=',int(low))).where(filter=FieldFilter('cost','<=',int(high)))
    
    if not user_token:
        return templates.TemplateResponse('main.html',{'request': request,'user_token': user_token,'error_message': "no error", 'user_info':None, 'ev_list':query.stream()})

    user = getUser(user_token).get()
    return templates.TemplateResponse('main.html',{'request': request,'user_token': user_token,'error_message': "no error", 'user_info':user, 'ev_list':query.stream()})

@app.post("/filter-by-power", response_class=HTMLResponse)
async def filterByPower(request: Request):
# there should be a token. Validate it and if invalid then redirect back to / as a basic security measure
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token)
    

    form = await request. form()
    low = form['lowpower']
    high = form['highpower']
    if not low or not high:
        return RedirectResponse('/', status_code=status.HTTP_302_FOUND)


    dummy_data_ref = firestore_db.collection('evdata')
    query = dummy_data_ref.where(filter=FieldFilter('power','>=',int(low))).where(filter=FieldFilter('power','<=',int(high)))
    
    if not user_token:
        return templates.TemplateResponse('main.html',{'request': request,'user_token': user_token,'error_message': "no error", 'user_info':None, 'ev_list':query.stream()})

    user = getUser(user_token).get()
    return templates.TemplateResponse('main.html',{'request': request,'user_token': user_token,'error_message': "no error", 'user_info':user, 'ev_list':query.stream()})

@app.post("/filter-by-year", response_class=HTMLResponse)
async def filterByYear(request: Request):
# there should be a token. Validate it and if invalid then redirect back to / as a basic security measure
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token)
    

    form = await request. form()
    low = form['lowyear']
    high = form['highyear']
    if not low or not high:
        return RedirectResponse('/', status_code=status.HTTP_302_FOUND)


    dummy_data_ref = firestore_db.collection('evdata')
    query = dummy_data_ref.where(filter=FieldFilter('year','>=',int(low))).where(filter=FieldFilter('year','<=',int(high)))
    
    if not user_token:
        return templates.TemplateResponse('main.html',{'request': request,'user_token': user_token,'error_message': "no error", 'user_info':None, 'ev_list':query.stream()})

    user = getUser(user_token).get()
    return templates.TemplateResponse('main.html',{'request': request,'user_token': user_token,'error_message': "no error", 'user_info':user, 'ev_list':query.stream()})

#Information Page for selected EV car
@app.get("/view-ev", response_class=RedirectResponse)
async def viewcar(request: Request):
# there should be a token. Validate it and if invalid then redirect back to / as a basic security measure
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token)
    

# pull the index from our form
#    form = await request. form()
#   search = form['viewname']

    search=request.query_params.get('viewname')
    print(search)


    
    dummy_data_ref = firestore_db.collection('evdata')
    query = dummy_data_ref.where(filter=FieldFilter('name','==',search))

    #finding average rating
    evcar=query.stream()
    evcar = next(evcar)
    array = evcar.get('rating')
    arr_int = [int(x) for x in array]
    if len(arr_int) == 0:
        average = -1
    else:
        average = sum(arr_int) / len(arr_int)

    if not user_token:
        return templates.TemplateResponse('viewcar.html',{'request': request,'user_token': user_token,'error_message': "no error", 'user_info':None, 'ev_list':query.stream(),'average':average})

    user = getUser(user_token).get()
    return templates.TemplateResponse('viewcar.html',{'request': request,'user_token': user_token,'error_message': "no error", 'user_info':user, 'ev_list':query.stream(),'average':average})









@app.post("/edit-ev", response_class=RedirectResponse)
async def editEV(request: Request):
    # Validate user token
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token)
    if not user_token:
        return RedirectResponse('/')

    # Retrieve form data
    form = await request.form()
    name = form['oldevname']

    # Retrieve existing EV data
    evcars_ref = firestore_db.collection('evdata').where('name', '==', name).get()

    for evcar_doc in evcars_ref:
        evcar_data = evcar_doc.to_dict()
        evcar_id = evcar_doc.id

        # Update the EV data except for 'review' and 'rating'
        evcar_data['name'] = form['name']
        evcar_data['manufact'] = form['manufact']
        evcar_data['year'] = int(form['year'])
        evcar_data['battery'] = int(form['battery'])
        evcar_data['wltp'] = int(form['wltp'])
        evcar_data['cost'] = int(form['cost'])
        evcar_data['power'] = int(form['power'])

        # Update Firestore with the modified EV data
        firestore_db.collection('evdata').document(evcar_id).set(evcar_data)

    # Redirect to home page
    return RedirectResponse('/', status_code=status.HTTP_302_FOUND)





#comparison page
@app.post("/comparison", response_class=RedirectResponse)
async def viewcar(request: Request):
# there should be a token. Validate it and if invalid then redirect back to / as a basic security measure
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token)
    

# pull the index from our form
    form = await request. form()
    option1 = form['option1']
    option2 = form['option2']

    

# pull the list of address objects from the user delete the requested index and update the user
    
    dummy_data_ref = firestore_db.collection('evdata')
    query1 = dummy_data_ref.where(filter=FieldFilter('name','==',option1))
    query2 = dummy_data_ref.where(filter=FieldFilter('name','==',option2))
    evcar1=query1.stream()
    evcar1 = next(evcar1)
    evcar2=query2.stream()
    evcar2 = next(evcar2)

    array1 = evcar1.get('rating')
    arr_int1 = [int(x) for x in array1]
    if len(arr_int1) == 0:
        average1 = -1
    else:
        average1 = sum(arr_int1) / len(arr_int1)

    array2 = evcar2.get('rating')
    arr_int2 = [int(x) for x in array2]
    if len(arr_int2) == 0:
        average2 = -1
    else:
        average2 = sum(arr_int2) / len(arr_int2)

    if not user_token:
        return templates.TemplateResponse('comparison.html',{'request': request,'user_token': user_token,'error_message': "no error", 'user_info':None, 'evcar1':evcar1, 'evcar2':evcar2,'average1':average1,'average2':average2})

    user = getUser(user_token).get()
    return templates.TemplateResponse('comparison.html',{'request': request,'user_token': user_token,'error_message': "no error", 'user_info':user, 'evcar1':evcar1,'evcar2':evcar2,'average1':average1,'average2':average2})


@app.post("/review-ev", response_class=RedirectResponse)
async def reviewEV(request: Request):
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token)
    if not user_token:
        return RedirectResponse('/')

    # pull the form containing our data
    form = await request.form()
    name = form['oldname']

    # Query Firestore to retrieve the document with matching name
    evcar_ref = firestore_db.collection('evdata').where('name', '==', name).get()

    # Assuming there is only one document with the given name
    for doc in evcar_ref:
        evcar_data = doc.to_dict()
        review = evcar_data.get('review', [])
        new_review = form['review']
        review.insert(0,new_review)

        # Update the review field in Firestore
        doc.reference.update({'review': review})

    # Redirect to home page after updating the review
    return RedirectResponse('/', status_code=status.HTTP_302_FOUND)

@app.post("/rating-ev", response_class=RedirectResponse)
async def ratingEV(request: Request):
    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token)
    if not user_token:
        return RedirectResponse('/')

    # pull the form containing our data
    form = await request.form()
    name = form['oldname']

    # Query Firestore to retrieve the document with matching name
    evcar_ref = firestore_db.collection('evdata').where('name', '==', name).get()

    # Assuming there is only one document with the given name
    for doc in evcar_ref:
        evcar_data = doc.to_dict()
        rating = evcar_data.get('rating', [])
        new_rating = form['rating']
        rating.insert(0,new_rating)

        # Update the review field in Firestore
        doc.reference.update({'rating': rating})

    # Redirect to home page after updating the review
    return RedirectResponse('/', status_code=status.HTTP_302_FOUND)
