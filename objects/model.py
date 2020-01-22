from google.cloud import automl

# The model object controls the connection to, API requests and, prediction of the GCP model 
class Model(object):
    def __init__(self, MODEL_CONFIG):
        # The projectID in Google Cloud
        self.project_id = MODEL_CONFIG['project_id']
        # The modelID of the model in the natural language section of GCP
        self.model_id = MODEL_CONFIG['model_id']
        # Creating a client to receive predictions
        self.client = automl.PredictionServiceClient()        
    
    def predict(self, text):
        """
        Receives a text input
        Outputs a payload with the prediction of the text sentiment
        """
        try:
            # All below is given code from GCP
            prediction_client = automl.PredictionServiceClient()  
            model_full_id = prediction_client.model_path(
                self.project_id, 'us-central1', self.model_id
            )

            text_snippet = automl.types.TextSnippet(
                content=text,
                mime_type='text/plain')  # Types: 'text/plain', 'text/html'
            payload = automl.types.ExamplePayload(text_snippet=text_snippet)

            response = prediction_client.predict(model_full_id, payload)
            return response.payload
        except Exception as error:
            print(error)
