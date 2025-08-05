from jipso._Judgement import _Judgement

class Judgement:
  """Represents the AI system or evaluator performing analysis.
  
  The Judgement component (J) encapsulates the reasoning entity - whether it's
  an AI model, human expert, or ensemble of evaluators. This class manages
  AI platform connections, evaluation methodologies, and consensus mechanisms
  for systematic AI evaluation workflows.
  
  Supports multiple AI platforms including Anthropic, OpenAI, Google, and local
  deployments. Enables ensemble operations with weighted voting and distributed
  consensus building for enhanced reliability and bias reduction.
  """

  def __init__(self, model):
    self._j = _Judgement(model)

  def __call__(self, i=None, p=None, s=None):
    return self._j(i,p,s)
