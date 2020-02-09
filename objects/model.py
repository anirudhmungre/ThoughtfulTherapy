from google.cloud.automl import PredictionServiceClient, types

# The model object controls the connection to, API requests and, prediction of the GCP model 
class Model(object):
    def __init__(self, MODEL_ID, CREDENTIALS):
        # The modelID of the model in the natural language section of GCP
        self.model_id = MODEL_ID
        # Creating a client to receive predictions
        self.credentials = CREDENTIALS       
    
    def predict(self, text):
        """
        Receives a text input
        Outputs a payload with the prediction of the text sentiment
        """
        try:
            # All below is given code from GCP
            prediction_client = PredictionServiceClient(credentials=self.credentials)  
            text_snippet = types.TextSnippet(
                content=text,
                mime_type='text/plain')  # Types: 'text/plain', 'text/html'
            payload = types.ExamplePayload(text_snippet=text_snippet)
            response = prediction_client.predict(self.model_id, payload)
            return response.payload
        except Exception as error:
            print(error)
