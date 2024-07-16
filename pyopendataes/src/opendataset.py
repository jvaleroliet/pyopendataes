import pandas as pd
import numpy as np
import requests


class OpenDataSet:
    def __init__(self, url:str):
        self.url = url
        self.id = url.split('/')[-1]
        # self.metadata = {}
    
    def __repr__(self):
        return f"OpenDataSet('{self.id}')"
    
    @property    
    def metadata(self):
        # Fetch metadata from the API
        response = requests.get(f"http://datos.gob.es/apidata/catalog/dataset/{self.id}")
        return response.json()["result"]["items"][0]
        

    @property
    def publisher_data_url(self):
        return self.metadata.get('identifier')

    @property
    def title(self):
        # Extract all title values based on language code
        titles = {d['_lang']: d['_value'] for d in self.metadata.get('title', [])}
        return titles

    @property
    def description(self):
        # Extract the first description value for each language
        descriptions = {d['_lang']: d['_value'] for d in self.metadata.get('description', [])}
        return descriptions

    @property
    def keywords(self):
        # Group keywords by language and remove duplicates
        keywords = {}
        for entry in self.metadata.get('keyword', []):
            lang_code = entry['_lang']
            keyword = entry['_value']
            keywords.setdefault(lang_code, set()).add(keyword)
        return {lang: list(values) for lang, values in keywords.items()}

    @property
    def distributions(self):
        """
        Returns a list of Distribution objects, each containing information for a single distribution.
        """
        distributions = self.metadata.get('distribution', [])
        distribution_objects = []
        for distribution_data in distributions:
            distribution_objects.append(Distribution(distribution_data))
        return distribution_objects

    def get_distribution_by_format(self, format):
        """
        Returns the distribution information for a specific format (e.g., text/csv).
        """
        matched_distributions = []
        for distribution in self.distributions:
            if distribution.format == format:
                matched_distributions.append(distribution)
        return matched_distributions
    
    
class Distribution:
    def __init__(self, data):
        self.data = data
    
    def __repr__(self):
        return f"Distribution('{self.access_url}')"

    @property
    def access_url(self):
        return self.data.get('accessURL')

    @property
    def byte_size(self):
        return self.data.get('byteSize')

    @property
    def format(self):
        return self.data.get('format')['value']

    @property
    def titles(self):
        # Extract title information for all languages efficiently
        return {d['_lang']: d['_value'] for d in self.data.get('title', [])}