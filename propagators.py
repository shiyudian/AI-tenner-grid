#Look for #IMPLEMENT tags in this file. These tags indicate what has
#to be implemented to complete problem solution. 

from collections import deque 

'''This file will contain different constraint propagators to be used within 
   bt_search.

   propagator == a function with the following template
      propagator(csp, newVar=None)
           ==> returns (True/False, [(Variable, Value), (Variable, Value) ...]

      csp is a CSP object---the propagator can use this to get access
      to the variables and constraints of the problem. The assigned variables
      can be accessed via methods, the values assigned can also be accessed.

      newVar (newly instaniated variable) is an optional argument.
      if newVar is not None:
          then newVar is the most
           recently assigned variable of the search.
      else:
          progator is called before any assignments are made
          in which case it must decide what processing to do
           prior to any variables being assigned. SEE BELOW

       The propagator returns True/False and a list of (Variable, Value) pairs.
       Return is False if a deadend has been detected by the propagator.
       in this case bt_search will backtrack
       return is true if we can continue.

      The list of variable values pairs are all of the values
      the propagator pruned (using the variable's prune_value method). 
      bt_search NEEDS to know this in order to correctly restore these 
      values when it undoes a variable assignment.

      NOTE propagator SHOULD NOT prune a value that has already been 
      pruned! Nor should it prune a value twice

      PROPAGATOR called with newVar = None
      PROCESSING REQUIRED:
        for plain backtracking (where we only check fully instantiated 
        constraints) 
        we do nothing...return true, []

        for forward checking (where we only check constraints with one
        remaining variable)
        we look for unary constraints of the csp (constraints whose scope 
        contains only one variable) and we forward_check these constraints.

        for gac we establish initial GAC by initializing the GAC queue
        with all constaints of the csp


      PROPAGATOR called with newVar = a variable V
      PROCESSING REQUIRED:
         for plain backtracking we check all constraints with V (see csp method
         get_cons_with_var) that are fully assigned.

         for forward checking we forward check all constraints with V
         that have one unassigned variable left

         for gac we initialize the GAC queue with all constraints containing V.
   '''

def prop_BT(csp, newVar=None):
    '''Do plain backtracking propagation. That is, do no 
    propagation at all. Just check fully instantiated constraints'''
    
    if not newVar:
        return True, []
    for c in csp.get_cons_with_var(newVar):# return list of constraints that include var in their scope
        if c.get_n_unasgn() == 0:   #        return the number of unassigned variables in the constraint's scope
            vals = []
            vars = c.get_scope()    #        return list(self.scope)
            for var in vars:
                vals.append(var.get_assigned_value())#return assigned value...returns None if is unassigned
            if not c.check(vals):   #        return tuple(vals) in self.sat_tuples
                return False, []
    return True, []

def FCCheck (csp, testVar):
    # csp is a constraint with all its variables already assigned, except for testVar
    pruned = []
    for val in testVar.cur_domain():
        testVar.assign(val)                 
        if not prop_BT(csp,testVar)[0]: #if not True
            testVar.prune_value(val)       # '''Remove value from CURRENT domain'''
            pruned.append((testVar, val))
        testVar.unassign()        #'''Used by bt_search. Unassign and restore old curdom'''
    # check domain wrap out
    if testVar.cur_domain_size() == 0:   #  '''Return the size of the variables domain (without construcing list)'''
        return False, pruned
    else:
        return True, pruned


def prop_FC(csp, newVar=None):
    '''Do forward checking. That is check constraints with 
       only one uninstantiated variable. Remember to keep 
       track of all pruned variable,value pairs and return '''
    pruned = []
    check_list = []
    if not newVar: #if not None
        check_list = csp.get_all_cons() # all constraints
    else:
        check_list = csp.get_cons_with_var(newVar)
        
    for c in check_list:
        if c.get_n_unasgn() !=1:   # '''return the number of unassigned variables in the constraint's scope'''
            continue
        testVar = c.get_unasgn_vars()[0] 
       # '''return list of unassigned variables in constraint's scope. Note
       #    more expensive to get the list than to then number'''
        to_prune = FCCheck(csp, testVar)    #pruned -> list
        pruned += to_prune[1]
        if not to_prune[0]:# True
            return False, pruned
    return True, pruned
            
#IMPLEMENT

def GAC_Enforce(csp,check_list):
    pruned = []
    queue = deque(check_list)
    while len(queue) != 0:
        c = queue.popleft()
        for var in c.scope:
            for val in var.cur_domain():
                if c.has_support(var,val):
                    continue
                # prune
                var.prune_value(val)
                pruned.append((var,val))
                if var.cur_domain_size() == 0:
                    queue.clear()
                    return False, pruned # first check does not work, clear
                else:
                    for new_cons in csp.get_cons_with_var(var):
                        if new_cons in queue:
                            continue
                        queue.append(new_cons)
    return True, pruned
                            

def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce 
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''

    check_list = []
    if not newVar:
        check_list = csp.get_all_cons()
    else:
        check_list = csp.get_cons_with_var(newVar)

    return GAC_Enforce(csp, check_list)
#IMPLEMENT
