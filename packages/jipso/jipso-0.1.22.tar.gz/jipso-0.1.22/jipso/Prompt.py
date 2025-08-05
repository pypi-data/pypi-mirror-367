from jipso._Judgement import _Judgement



class Prompt:
  """Encapsulates instructions and methodology for AI execution.
  
  The Prompt component (P) defines HOW tasks should be performed - methodology,
  approach, and specific instructions. Provides systematic prompt engineering
  capabilities including decomposition for complex workflows and union operations
  for modular prompt construction.
  
  Enables natural language programming through conversational prompt development,
  iterative improvement cycles, and template-based prompt optimization. Supports
  role assignment, few-shot learning integration, and constraint specification
  for precise AI behavior control.
  """

  def __init__(self, data, model='gpt-4-turbo'):
    self.data = data
    self.j = _Judgement(model)

  def __str__(self): return self.data

  # ----------------------------------------
  # Set vs Element
  # ----------------------------------------

  def add(self, item, replace=False):
    if isinstance(item, str):
      o = self.j(p='Please add component x to Prompt P', i=f'P: {self.data}\nx: {item}')
    if replace:
      self.data = o
    return o
  
  def remove(self, item): pass
  def __contains__(self, item): pass
  def __len__(self): pass
  def __iter__(self): pass
  def __next__(self): pass

  # ----------------------------------------
  # Set vs Set
  # ----------------------------------------
  def __or__(self, other, replace=False):
    if isinstance(other, Prompt):
      p2 = p2.data
    o = self.j(p='Combine the content of Prompt P2 into Prompt P1', i=f'P1: {self.data}\nP2: {p2}')
    if replace:
      self.data = o
    return o
  def __and__(self, other): pass
  def __sub__(self, other): pass
  def __xor__(self, other): pass

  # ----------------------------------------
  # Compare Set
  # ----------------------------------------
  def __eq__(self, other): pass
  def __ne__(self, other): pass
  def __lt__(self, other): pass
  def __le__(self, other): pass
  def __gt__(self, other): pass
  def __ge__(self, other): pass

  # ----------------------------------------
  # Special
  # ----------------------------------------
  def __invert__(self): pass
  def set(self): pass
  def tuple(self): pass
  def to_json(self): pass
  def to_text(self): pass