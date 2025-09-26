# import pandas as pd
# import json
# import re

# def build_headline(pillar:str, scope:str, headline:str):
#     scope = scope.upper()
#     #Read in the pillars
#     pillars_list = pd.read_csv("agent/sources/strategic_pillars.csv", usecols=[0]).iloc[:, 0].tolist()
#     if pillar.title() not in pillars_list:
#         return False
#     if scope.upper() != "GLOBAL":
#         if not check_regional_accuracy(scope):
#             raise Exception(f"{scope} has not been properly formatted. Must be 'GLOBAL', a region, or a region / country which matches supported scopes.")
#     return(f"{pillar.upper() [scope]: {headline.title()}}")    

# def check_regional_accuracy(scope:str):
#     """
#     Determines if 'scope' was properly defined per geographic mappings

#     Args:
#         Scope: The LLM defined geographic area of interest. 
#     Returns:
#         True: iIf all checks pass
#         False: If 'scope' cannot be found in reference json
#     """
#     data = json.load("agent/sources/supported_scopes.json")
#     match = re.search(r"(.+)\/(.+)", scope)
#     if not match:
#         if not scope in data['regions']:
#             return False
#         else:
#             return True
#     else:
#         if not match.group(1).replace(" ","") in data['regions']:    
#             return False
#         elif not match.group(2).replace(" ","") in data['countries']:  
#             return False
#         else:
#             return True  
        


        