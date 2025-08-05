import os, ujson

class _Judgement:
  def __init__(self, id):
    self.id = id
    models_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'models.json'))
    with open(models_path, 'r') as f: models = ujson.load(f)
    if self.id not in models:
      raise ValueError(f'Model {self.id} not exsits')
    
    self.platform = models[self.id]['platform']
    if self.platform == 'Openai':
      from jipso.Client import ClientOpenai
      self.client = ClientOpenai()
    elif self.platform == 'Anthropic':
      from jipso.Client import ClientAnthropic
      self.client = ClientAnthropic()
    elif self.platform == 'Gemini':
      from jipso.Client import ClientGemini
      self.client = ClientGemini()
    elif self.platform == 'Xai':
      from jipso.Client import ClientXai
      self.client = ClientXai()
    elif self.platform == 'Alibabacloud':
      from jipso.Client import ClientAlibabacloud
      self.client = ClientAlibabacloud()
    elif self.platform == 'Byteplus':
      from jipso.Client import ClientByteplus
      self.client = ClientByteplus()
    elif self.platform == 'Sberbank':
      from jipso.Client import ClientSberbank
      self.client = ClientSberbank()

  def __call__(self, i=None, p=None, s=None):
    text = '\n'.join(filter(None, [p, s, i]))
    if self.platform == 'Openai':
      res = self.client.chat.completions.create(
        model = self.id,
        messages = [
          {'role': 'user', 'content': text}
        ]
      )
      return res.choices[0].message.content
    elif self.platform == 'Anthropic':
      res = self.client.messages.create(
        model = self.id,
        max_tokens = 100,
        messages = [
          {'role': 'user', 'content': text}
        ]
      )
      return res.content[0].text
    elif self.platform == 'Gemini':
      res = self.client.GenerativeModel('models/gemini-2.0-flash').generate_content(text)
      return res._result.candidates[0].content.parts[0].text
