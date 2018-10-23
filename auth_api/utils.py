from social_core.pipeline.user import create_user as social_create_user

USER_FIELDS = ['username', 'email' 'id', 'gender']

def create_user(strategy, details, backend, user=None, *args, **kwargs):
    if not user:

        try:
            sexo = kwargs['response']['gender']
            if sexo == 'male':
                details['genero'] =  'M'
            else:
                details['genero'] = 'F'    
            
        except:
            pass

        try:  
            details['facebook_id'] = kwargs['response']['id']  
        except:
            pass    
 
    result = social_create_user(strategy, details, backend, user=None, *args, **kwargs)
    return result



