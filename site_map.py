#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 10:34:24 2020

@author: Home
"""

import os
import pandas as pd

import requests
import re
from bs4 import BeautifulSoup


class site_network:
    
    def __init__(self, base_url, file_path):
        
        #This app requires two things:
        #1. A website URL to start the search with
        #2. A file path to save the Nodes and Edges to
        self.base_url = base_url
        self.file_path = file_path
        
               
    def get_website(self):        
        
        #inner function to collect links from a webpage
        def get_page(url):            
            #use request to get url data
            page_response = requests.get(url)
    
            #parse the page content based on html structure
            page_content = BeautifulSoup(page_response.content, "html.parser")
            
            #this find all links that have the searched for url within it
            #need to check to see if this is inadvertently limiting application ability
            all_links = page_content.find_all("a", href=re.compile('^('+url+')'))
            
            #this parses out the linking urls
            links = []
            for i in range(0, len(all_links)):
                links.append(all_links[i].get('href'))
            #deduplicates list    
            links = [x for x in set(links)]
            
            return links
        
        
        #create the directory where the data will be saved down    
        os.mkdir(self.file_path)
               
        #get the initial page and links
        links = get_page(self.base_url)
        
        #create a dataframe with the original url and all linking urls within that page
        page_links = pd.DataFrame({"Primary":self.base_url,
                                   "Secondary":links})
        
        #create an empty list to track all collected links
        #this is necessary because the search is recursive in nature
        check_list = []    
        
        #create an potentially infinite loop to begin the search
        while True:
            
            #begin to iterate through the list of links collected from the original search
            for i in range(0, len(links)):
                
                #check if the link we are about to search for is in the recursive opt out check list
                if links[i] not in check_list:
                    
                    #add the new url link to the check list for future iteration, this will prevent requesting the same page twice
                    check_list.append(links[i])
                    
                    #request the link
                    inner_links = get_page(links[i])
                    
                    #print function to keep track of pregress
                    print(links[i])                   
                    
                    #create the data frame of node and edges
                    link_df = pd.DataFrame({"Primary":links[i],
                                       "Secondary":inner_links})
                    #append the new dataframe to existing dataframe of links
                    page_links = page_links.append(link_df)
            
                    #add any new links collected to the existing link list which is being searched
                    for i in range(0, len(inner_links)):
                        if inner_links[i] not in links:
                            links.append(inner_links[i])
            
            #this ends the recursive search
            #while this is false the link list in the original for loop will continue to grow            
            if len(check_list) == len(links):
                break           
        
        #save the all of the collected nodes and edges into a csv
        page_links.to_csv(self.file_path+'/Links.csv', index=False)



site_network('https://www.mysticaquarium.org/', 
             '/Users/Home/Desktop/Projects/Text_Projects/web_scraping/Mystic_Aquarium').get_website()


