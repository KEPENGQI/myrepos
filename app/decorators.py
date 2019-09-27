from flask import request, redirect
import urllib.parse
import urllib.request
import functools
import json
import urllib
import jinja2


cas_url = 'https://cas.apiit.edu.my/cas'
cas_attrs = ['sAMAccountName', 'distinguishedName']
CAS_service_validation_url = 'https://cas.apiit.edu.my/cas/p3/serviceValidate?format=json&'


def login_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if 'ticket' not in request.args:
            return redirect(f'{cas_url}/login?service={request.base_url}')
        ticket = str(jinja2.escape(request.args.get('ticket')))
        query = urllib.parse.urlencode({
            'format': 'json',
            'ticket': ticket,
            'service': request.base_url
        })
        with urllib.request.urlopen(f'{cas_url}/p3/serviceValidate?{query}') as url:
            data = json.load(url).get('serviceResponse')
            if 'authenticationSuccess' not in data:
                return redirect(f'{cas_url}/login?service={request.base_url}')
            a = data['authenticationSuccess']['attributes']
            for k in a:
                if k in cas_attrs: kwargs['cas:' + k] = a[k][0]
        return f(*args, **kwargs)
    return wrapper