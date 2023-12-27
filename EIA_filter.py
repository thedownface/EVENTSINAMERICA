from concurrent.futures import ThreadPoolExecutor
import json
import os
from Variables import Variable
import pandas as pd
from Email_Verifier import Verifier

facts=Variable.get('EventsInAmerica')

def Email_Verifier(email):
    try:
        v=Verifier(email)
        if v['deliverable']==True:
            return True
        elif v['host_exists']==True:
            return True
    except:
        return True
    
    

def filter_email(df):
    
   
    try:
        emails=df['Email']
        emails=emails.drop_duplicates(keep=False)
        with ThreadPoolExecutor() as executor:
            verified_emails = list(executor.map(Email_Verifier, emails))
        verified_df = pd.DataFrame({'Email': verified_emails, 'PROVIDER': df['PROVIDER'][0]})
        return verified_df
                

                
    except Exception as e:
        print(f'Exception:{e}')