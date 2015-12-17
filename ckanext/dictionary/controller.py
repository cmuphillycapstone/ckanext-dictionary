import logging
import ckan.plugins as p
from ckan.lib.base import BaseController
import ckan.lib.helpers as h
from ckan.common import OrderedDict, _, json, request, c, g, response
from urllib import urlencode
import datetime
import mimetypes
import cgi


import ckan.logic as logic
import ckan.lib.base as base
import ckan.lib.maintain as maintain
import ckan.lib.i18n as i18n
import ckan.lib.navl.dictization_functions as dict_fns
#import ckan.lib.accept as accept
#import ckan.lib.helpers as h
import ckan.model as model
import ckan.lib.datapreview as datapreview
import ckan.lib.plugins
import ckan.lib.uploader as uploader
import ckan.plugins as p
import ckan.lib.render

#render = ckan.lib.base.render
#from home import CACHE_PARAMETERS

log = logging.getLogger(__name__)

render = base.render
abort = base.abort
redirect = base.redirect


NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
check_access = logic.check_access
get_action = logic.get_action
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params
flatten_to_string_key = logic.flatten_to_string_key

lookup_package_plugin = ckan.lib.plugins.lookup_package_plugin


class DDController(BaseController):

    def index(self):
	#print(sys.path)
	return p.toolkit.render("base1.html")
    
    def _resource_form(self, package_type):
        # backwards compatibility with plugins not inheriting from
        # DefaultDatasetPlugin and not implmenting resource_form
        plugin = lookup_package_plugin(package_type)
        if hasattr(plugin, 'resource_form'):
            result = plugin.resource_form()
            if result is not None:
                return result
        return lookup_package_plugin().resource_form()

	
    def finaldict(self, id, data=None, errors=None):
        if request.method== 'POST':
            print("!!!!!!!!!!!!!!!!!!1 POsted FROM EXTENSION!!!!!!!!!!!1")
            #print(request.params.get())
        c.link = str("/dataset/dictionary/new_dict/"+id)
	return render("package/new_data_dict.html",extra_vars={'package_id':id})
    def edit_dictionary(self, id, data=None, errors=None):
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'for_view': True,
                   'auth_user_obj': c.userobj, 'use_cache': False}
	resource_ids = None
        try:
	    meta_dict = {'resource_id': '_table_metadata'}
	    tables = get_action('datastore_search')(context,meta_dict)
	    for t in tables['records']:
	        print(t['name'])
	        if t['name'] == "data_dict":
		    resource_ids = t['alias_of']
	except:
	    resource_ids == None
	if resource_ids == None:
	    create = {'resource':{'package_id':id},'aliases':'data_dict','fields':[{'id':'package_id', 'type':'text'},{'id':'id','type':'int4'},{'id':'title','type':'text'},{'id':'field_name','type':'text'},{'id':'format','type':'text'},{'id':'description','type':'text'}],'primary_key':['id']}
	    get_action('datastore_create')(context,create)
	    print("CREATE TABLE !!!!!!!!!!!!!!!!!!!!!!!IDID")
            meta_dict = {'resource_id': '_table_metadata'}
            tables = get_action('datastore_search')(context,meta_dict)
            for t in tables['records']:
                print(t['name'])
                if t['name'] == "data_dict":
                    resource_ids = t['alias_of']
	data_dict_dict = {'resource_id': resource_ids,'filters': {'package_id':id},'sort':['id']}
        try:
	    print("EXTENSION LOCALLLLLLLLLLLLLLLLLLLLLLLL")
            pkg_data_dictionary = get_action('datastore_search')(context, data_dict_dict)
            #print(pkg_data_dictionary['records'])
            c.pkg_data_dictionary = pkg_data_dictionary['records']
	    c.link = str("/dataset/dictionary/new_dict/"  + id)
            c.pkg_dict = get_action('package_show')(context, {'id':id})
            c.pkg = context['package']
        except NotFound:
            abort(404, _('Dataset not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read dataset %s') % id)
        return render("package/edit_data_dict.html",extra_vars={'package_id':id})

    def redirectSecond(self, id, data=None, errors=None):
        return render("package/new_resource.html")
    def new_data_dictionary(self, id):
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!IN THE EXTENTION !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        if request.method == 'POST':
            save_action = request.params.get('save')
            print("new data dictionary !!!!!!!!!!!!!!!!")
            context = {'model': model, 'session': model.Session,
                       'user': c.user or c.author, 'auth_user_obj': c.userobj}
            counter = 0
            tempdata= ''
            ###########################
            resource_ids = None
            try:
                meta_dict = {'resource_id': '_table_metadata'}
                tables = get_action('datastore_search')(context,meta_dict)
                for t in tables['records']:
                    print(t['name'])
                    if t['name'] == "data_dict":
                        resource_ids = t['alias_of']
            except:
	        resource_ids = None
	    if resource_ids == None:
                create = {'resource':{'package_id':id},'aliases':'data_dict','fields':[{'id':'package_id','type':'text'},{'id':'id','type':'int4'},{'id':'title','type':'text'},{'id':'field_name','type':'text'},{'id':'format','type':'text'},{'id':'description','type':'text'}],'primary_key':['id']}
                get_action('datastore_create')(context,create)
	        print("CREATE TABLE` !!!!!!!!!!!!!!!!!!!!!!!")
                meta_dict = {'resource_id': '_table_metadata'}
                tables = get_action('datastore_search')(context,meta_dict)
                for t in tables['records']:
                    print(t['name'])
                    if t['name'] == "data_dict":
                        resource_ids = t['alias_of']
	    print("PACKAGEID ",id)
            data_dict_dict = {'resource_id': resource_ids,'filters': {'package_id':id},'sort':['id']}

            records=[]
            try:
		print("IM HERE>>>>>>>>>>>>>>>>>>>>>>")
                pkg_data_dictionary = get_action('datastore_search')(context, data_dict_dict)
                records=pkg_data_dictionary['records']
            except NotFound:
                abort(404, _('Dataset not found'))
            except NotAuthorized:
                abort(401, _('Unauthorized to read dataset %s') % id)

            ###########################
            if records==[]:
                data_dict_table = {'resource_id': resource_ids}
                maxID_data = get_action('datastore_search')(context, data_dict_table)
                maxID_records = maxID_data['records']
                maxID = 0
                for record in maxID_records:
        	    print(record['id'])
	            maxID = max(maxID, record['id'])
		print("MAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAX ID: ",maxID)
                while tempdata != None:
                        varNames = ['field_'+str(counter), 'type_'+str(counter), 'description_'+str(counter), 'format_'+str(counter), 'title_'+str(counter),]
                        tempdata = request.params.get(varNames[0])
                        datafield = request.params.get(varNames[0])
                        datatype = request.params.get(varNames[1])
                        datadesc = request.params.get(varNames[2])
                        dataformat = request.params.get(varNames[3])
                        datatitle = request.params.get(varNames[4])
                        tdata = {'resource_id':resource_ids, 'records':[{'package_id' : id, 'field_name':datafield, 'description':datadesc, "title":datatitle, "format":dataformat, 'id' : maxID+counter+1}], 'method': 'upsert'}
                        print("datafield: ",datafield," datatype: ",datatype," datadesc: ",datadesc)
                        if datafield!=None or datatype!=None or datadesc!=None or datatitle!=None or dataformat!=None:
                                if datafield!='' or datatype!='' or datadesc!='' or datatitle!='' or dataformat!='':
                                        get_action('datastore_upsert')(context,  tdata)
                        print(tempdata)
                        counter = counter +1
            else:
                 data_dict_table = {'resource_id': resource_ids}
                 maxID_data = get_action('datastore_search')(context, data_dict_table)
                 maxID_records = maxID_data['records']
                 maxID = 0
                 for record in maxID_records:
		        print(record['id'])
                        maxID = max(maxID, record['id']+0)
		 print(maxID)
                 #counter=0
                 #countHelper='field_'+str(counter)
                 #idHelper='id_'+str(counter)
                 #editedIds=[]
                 #tempdata=tempdata=request.params.get(countHelper)
                 #while tempdata != None:
                 #       varNames = ['field_'+str(counter), 'type_'+str(counter), 'description_'+str(counter), 'sensitivity_'+str(counter), 'id_'+str(counter)]
                 #       print("ID: ",request.params.get(idHelper))
                 #       editedIds.append(request.params.get(idHelper))
                 #       counter+=1
                 #       countHelper='field_'+str(counter)
                 #       idHelper='id_'+str(counter)
                 #       print("CONUTHELPER: ",countHelper)
                 #       print("TEMPDATA: ",tempdata)

                 #       tempdata=request.params.get(countHelper)
                 #print("PRIMARY KEYS ARE: ",editedIds)
                 #tempdata= ''
                 addCounter=1
                 while tempdata != None:
                        varNames = ['field_'+str(counter), 'type_'+str(counter), 'description_'+str(counter), 'title_'+str(counter), 'format_'+str(counter), 'id_'+str(counter)]
                        tempdata = request.params.get(varNames[0])
                        datafield = request.params.get(varNames[0])
                        datatype = request.params.get(varNames[1])
                        datadesc = request.params.get(varNames[2])
                        datatitle =request.params.get(varNames[3])
                        dataformat = request.params.get(varNames[4])
                        dataid = request.params.get(varNames[5])
                        tdata = {'resource_id':resource_ids, 'records':[{'package_id' : id, 'field_name':datafield, 'description':datadesc, "title":datatitle, "format": dataformat,"id":dataid}], 'method': 'update','force':True}
                        #print("datafield: ",datafield," datatype: ",datatype," datadesc: ",datadesc," datasens: ",datasens," dataiid: ",dataid)
			if datafield!=None or datatype!=None or datadesc!=None or datatitle!= None or dataformat!=None:
                                if datafield!='' or datatype!='' or datadesc!='' or datatitle!='' or dataformat!='':
                                     #print("FOUR VAUES NOT BLANK")
                                     if dataid!='' and dataid!=None:
                                        #print("FOUR VALUES NOT BLANK AND ID EXISTS ",dataid)
                                        get_action('datastore_upsert')(context,  tdata)
                                     else:
                                        tdata1 = {'resource_id':resource_ids, 'records':[{'package_id' : id, 'field_name':datafield, 'description':datadesc, "title":datatitle, "format":dataformat,'id' : maxID+addCounter}], 'method': 'insert'}
                                        print("uperst !!!!!!!!" + datatitle + str(maxID))
				        get_action('datastore_upsert')(context,  tdata1)
				        print("success")
                                        addCounter+=1
                                else:
                                     #print("FOUR VALUES BLANK")
                                     req={'resource_id':resource_ids,'filters': {'id':dataid}}
                                     get_action('datastore_delete')(context, req)
                        print(tempdata)
                        counter = counter +1

            #data = request.params
            if save_action == 'go-add-dict':
                context = {'model': model, 'session': model.Session,
                       'user': c.user or c.author, 'auth_user_obj': c.userobj}
                data_dict = get_action('package_show')(context, {'id': id})
                get_action('package_update')(
                    dict(context, allow_state_change=True),
                    dict(data_dict, state='active'))
                redirect(h.url_for(controller='package',
                                   action='read', id=id))
            elif save_action == 'go-dataset':
                redirect(h.url_for(controller="package", action="new_resource", id=id))
        #print("!!!!!!!!!!! the value of temp is",temp, id)
        print("!!!!!!!!!!!!")
        redirect(h.url_for(controller='package', action='read', id=id))


    def new_resource_ext(self, id, data=None, errors=None, error_summary=None):
        ''' FIXME: This is a temporary action to allow styling of the
        forms. '''
	c.linkResource = str("/dataset/new_resource/"+id)
	print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! IN NEW_RESOURCE_EXT !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        if request.method == 'POST' and not data:
            save_action = request.params.get('save')
            #if save_action == 'go-datadict':
                #redirect(h.url_for(controller='package', action='addDictionary'))
            data = data or \
                clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(
                                                           request.POST))))
            # we don't want to include save as it is part of the form
            del data['save']
            #if 'id' in data.keys()and save_action=="go-dataset-final":
            #print("Id found","and the path is: ",request.path)
            resource_id = data['id']
            #redirect(h.url_for(controller='package',action='read',id=id))
            #request.path.split("/")[2]))
            #else:
            #print("In else part",id," and the request path is: ", request.path)
            #if save_action == 'go-dataset-final':
            #redirect(h.url_for(controller='package',action='new_resource',id=id))
            #request.path.split("/")[2]))

            del data['id']

            context = {'model': model, 'session': model.Session,
                       'user': c.user or c.author, 'auth_user_obj': c.userobj}

            # see if we have any data that we are trying to save

            data_provided = False
            for key, value in data.iteritems():
                if ((value or isinstance(value, cgi.FieldStorage))
                        and key != 'resource_type'):
                    data_provided = True
                    break
            if not data_provided and save_action != "go-dataset-complete":
                if save_action == 'go-dataset':
                    # go to final stage of adddataset
                    redirect(h.url_for(controller='package',
                                       action='edit', id=id))
                # see if we have added any resources
                try:
                    data_dict = get_action('package_show')(context, {'id': id})
                except NotAuthorized:
                    abort(401, _('Unauthorized to update dataset'))
                except NotFound:
                    abort(404, _('The dataset {id} could not be found.'
                                 ).format(id=id))
                if not len(data_dict['resources']):
                    # no data so keep on page
                    msg = _('You must add at least one data resource')
                    # On new templates do not use flash message
                    if g.legacy_templates:
                        h.flash_error(msg)
                        redirect(h.url_for(controller='package',
                                           action='new_resource', id=id))
                    else:
                        errors = {}
                        error_summary = {_('Error'): msg}
                        return self.new_resource_ext(id, data, errors,
                                                 error_summary)
                # XXX race condition if another user edits/deletes
                data_dict = get_action('package_show')(context, {'id': id})
                get_action('package_update')(
                    dict(context, allow_state_change=True),
                    dict(data_dict, state='active'))
                redirect(h.url_for(controller='package',
                                   action='read', id=id))

            data['package_id'] = id
            try:
                if resource_id:
                    data['id'] = resource_id
                    get_action('resource_update')(context, data)
                else:
                    get_action('resource_create')(context, data)
            except ValidationError, e:
                errors = e.error_dict
                error_summary = e.error_summary
                return self.new_resource(id, data, errors, error_summary)
            except NotAuthorized:
                abort(401, _('Unauthorized to create a resource'))
            except NotFound:
                abort(404, _('The dataset {id} could not be found.'
                             ).format(id=id))
            if save_action == 'go-metadata':
                # XXX race condition if another user edits/deletes
                data_dict = get_action('package_show')(context, {'id': id})
                get_action('package_update')(
                    dict(context, allow_state_change=True),
                    dict(data_dict, state='active'))
                redirect(h.url_for(controller='package',
                                   action='read', id=id))
            elif save_action == 'go-datadict':
                #if not len(data_dict['resources']):
                    # no data so keep on page
                    #msg = _('You must add at least one data resource')
                    # On new templates do not use flash message
                    #if g.legacy_templates:
                        #h.flash_error(msg)
                        #redirect(h.url_for(controller='package',action='new_resource', id=id))
                    #else:
                        #errors = {}
                        #error_summary = {_('Error'): msg}
                        #return self.new_resource(id, data, errors,
                                                 #error_summary)
                print('save action was go-datadict in the exntenstion NEEWWWW!!!!!!!!!!!')
                redirect(h.url_for(str("/dataset/dictionary/add/"+id)))
		#redirect(h.url_for(controller='package', action='finaldict', id=id))
            elif save_action == 'go-dataset':
                # go to first stage of add dataset
                redirect(h.url_for(controller='package',
                                   action='edit', id=id))
            elif save_action == 'go-dataset-complete':
                # go to first stage of add dataset
                redirect(h.url_for(controller='package',
                                   action='read', id=id))
            else:
                # add more resources
                redirect(h.url_for(controller='package',
                                   action='new_resource', id=id))

        # get resources for sidebar
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj}
        try:
            pkg_dict = get_action('package_show')(context, {'id': id})
        except NotFound:
            abort(404, _('The dataset {id} could not be found.').format(id=id))
        try:
            check_access(
                'resource_create', context, {"package_id": pkg_dict["id"]})
        except NotAuthorized:
            abort(401, _('Unauthorized to create a resource for this package'))

        package_type = pkg_dict['type'] or 'dataset'

        errors = errors or {}
        error_summary = error_summary or {}
        vars = {'data': data, 'errors': errors,
                'error_summary': error_summary, 'action': 'new',
                'resource_form_snippet': self._resource_form(package_type),
                'dataset_type': package_type}
        vars['pkg_name'] = id
        # required for nav menu
        vars['pkg_dict'] = pkg_dict
        template = 'package/new_resource_not_draft.html'
        if pkg_dict['state'].startswith('draft'):
            vars['stage'] = ['complete', 'active']
            template = 'package/new_resource.html'
        return render(template, extra_vars=vars)
    def dictionary(self, id):
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'for_view': True,
                   'auth_user_obj': c.userobj, 'use_cache': False}
        data_dict = {'id': id}
        try:
	    print("here!!!!!!!!1")
	    #tem = get_action('package_show')(context, data_dict)
	    #print(tem)
            c.pkg_dict = get_action('package_show')(context, data_dict)
            dataset_type = c.pkg_dict['type'] or 'dataset'
        except NotFound:
            abort(404, _('Dataset not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read dataset %s') % id)

        #if request.method == 'POST':
            #new_group = request.POST.get('group_added')
            #if new_group:
                #data_dict = {"id": new_group,
                             #"object": id,
                             #"object_type": 'package',
                             #"capacity": 'public'}
                #try:
                    #get_action('member_create')(context, data_dict)
                #except NotFound:
                    #abort(404, _('Group not found'))

            #removed_group = None
            #for param in request.POST:
                #if param.startswith('group_remove'):
                    #removed_group = param.split('.')[-1]
                    #break
            #if removed_group:
                #data_dict = {"id": removed_group,
                             #"object": id,
                             #"object_type": 'package'}

                #try:
                    #get_action('member_delete')(context, data_dict)
                #except NotFound:
                    #abort(404, _('Group not found'))
            #redirect(h.url_for(controller='package',
                               #action='groups', id=id))

        #context['is_member'] = True
        #users_groups = get_action('group_list_authz')(context, data_dict)

        #pkg_group_ids = set(group['id'] for group
                            #in c.pkg_dict.get('groups', []))
        #user_group_ids = set(group['id'] for group
                             #in users_groups)

        #c.group_dropdown = [[group['id'], group['display_name']]
                            #for group in users_groups if
                            #group['id'] not in pkg_group_ids]

        #for group in c.pkg_dict.get('groups', []):
            #group['user_member'] = (group['id'] in user_group_ids)

        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'for_view': True,
                   'auth_user_obj': c.userobj, 'use_cache': False}
        resource_ids = None
        try:
            meta_dict = {'resource_id': '_table_metadata'}
            tables = get_action('datastore_search')(context,meta_dict)
            for t in tables['records']:
                print(t['name'])
                if t['name'] == "data_dict":
                    resource_ids = t['alias_of']
	except:
	    resource_ids = None
        if resource_ids == None:
            create = {'resource':{'package_id':id},'aliases':'data_dict','fields':[{'id':'package_id','type':'text'},{'id':'id','type':'int4'},{'id':'title','type':'text'},{'id':'field_name','type':'text'},{'id':'format','type':'text'},{'id':'description','type':'text'}],'primary_key':['id']}
            get_action('datastore_create')(context,create)
	    print("CREATE TABLE !!!!!!!!!!!!!!!!!!!!!!!")
            meta_dict = {'resource_id': '_table_metadata'}
            tables = get_action('datastore_search')(context,meta_dict)
            for t in tables['records']:
                print(t['name'])
                if t['name'] == "data_dict":
                    resource_ids = t['alias_of']
        data_dict_dict = {'resource_id': resource_ids,'filters': {'package_id':id},'sort':['id']}
        try:
            pkg_data_dictionary = get_action('datastore_search')(context, data_dict_dict)
            print(pkg_data_dictionary['records'])
            c.pkg_data_dictionary = pkg_data_dictionary['records']
        except NotFound:
            abort(404, _('Dataset not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read dataset %s') % id)
        return render('package/dictionary_display.html',{'dataset_type': dataset_type})
