..
   Custom class template to make sphinx-autosummary list the full API doc after
   the summary. See https://github.com/sphinx-doc/sphinx/issues/7912

ExprCompiler
============

.. currentmodule:: guppylang.compiler.expr_compiler

.. autoclass:: ExprCompiler
   :members:
   :show-inheritance:
   :inherited-members:

   
   
   .. rubric:: Methods

   .. autosummary::
      :nosignatures:
   
      ~ExprCompiler.compile
      ~ExprCompiler.compile_row
      ~ExprCompiler.generic_visit
      ~ExprCompiler.visit
      ~ExprCompiler.visit_BinOp
      ~ExprCompiler.visit_Call
      ~ExprCompiler.visit_Compare
      ~ExprCompiler.visit_Constant
      ~ExprCompiler.visit_DesugaredArrayComp
      ~ExprCompiler.visit_DesugaredListComp
      ~ExprCompiler.visit_FieldAccessAndDrop
      ~ExprCompiler.visit_GenericParamValue
      ~ExprCompiler.visit_GlobalCall
      ~ExprCompiler.visit_GlobalName
      ~ExprCompiler.visit_InoutReturnSentinel
      ~ExprCompiler.visit_List
      ~ExprCompiler.visit_LocalCall
      ~ExprCompiler.visit_Name
      ~ExprCompiler.visit_PartialApply
      ~ExprCompiler.visit_PlaceNode
      ~ExprCompiler.visit_ResultExpr
      ~ExprCompiler.visit_SubscriptAccessAndDrop
      ~ExprCompiler.visit_TensorCall
      ~ExprCompiler.visit_Tuple
      ~ExprCompiler.visit_TypeApply
      ~ExprCompiler.visit_UnaryOp
   
   

   
   
   .. rubric:: Attributes

   .. autosummary::
   
      ~ExprCompiler.builder
      ~ExprCompiler.dfg
      ~ExprCompiler.globals
   
   