#Look for #IMPLEMENT tags in this file. These tags indicate what has
#to be implemented to complete the warehouse domain.  

'''
Construct and return Tenner Grid CSP models.
'''

from cspbase import *
import itertools
import numpy 

def tenner_csp_model_1(initial_tenner_board):
    '''Return a CSP object representing a Tenner Grid CSP problem along 
       with an array of variables for the problem. That is return

       tenner_csp, variable_array

       where tenner_csp is a csp representing tenner grid using model_1
       and variable_array is a list of lists

       [ [  ]
         [  ]
         .
         .
         .
         [  ] ]

       such that variable_array[i][j] is the Variable (object) that
       you built to represent the value to be placed in cell i,j of
       the Tenner Grid (only including the first n rows, indexed from 
       (0,0) to (n,9)) where n can be 3 to 8.
       
       
       The input board is specified as a pair (n_grid, last_row). 
       The first element in the pair is a list of n length-10 lists.
       Each of the n lists represents a row of the grid. 
       If a -1 is in the list it represents an empty cell. 
       Otherwise if a number between 0--9 is in the list then this represents a 
       pre-set board position. E.g., the board
    
       ---------------------  
       |6| |1|5|7| | | |3| |
       | |9|7| | |2|1| | | |
       | | | | | |0| | | |1|
       | |9| |0|7| |3|5|4| |
       |6| | |5| |0| | | | |
       ---------------------
       would be represented by the list of lists
       
       [[6, -1, 1, 5, 7, -1, -1, -1, 3, -1],
        [-1, 9, 7, -1, -1, 2, 1, -1, -1, -1],
        [-1, -1, -1, -1, -1, 0, -1, -1, -1, 1],
        [-1, 9, -1, 0, 7, -1, 3, 5, 4, -1],
        [6, -1, -1, 5, -1, 0, -1, -1, -1,-1]]
       
       
       This routine returns model_1 which consists of a variable for
       each cell of the board, with domain equal to {0-9} if the board
       has a -1 at that position, and domain equal {i} if the board has
       a fixed number i at that cell.
       
       model_1 contains BINARY CONSTRAINTS OF NOT-EQUAL between
       all relevant variables (e.g., all pairs of variables in the
       same row, etc.).
       model_1 also constains n-nary constraints of sum constraints for each 
       column.
    '''
        
    # process the input to have a board
    cell_rows,last_row = process_board(initial_tenner_board)
    num_rows = len(initial_tenner_board[0]) # n = number of rows, each row with 10 cols
        
    # define variables and add their domain values
    variable_array = make_var_array(cell_rows,num_rows)
    
##    
    # DEFINE CONSTRAINTS:
    # set up the constraints
    constraint_list = []
    #row constraints -> rows 3~8 rows; each row has no duplicates
    # can be computed as ALL-DIFF constraints as in soduko case - bi-nary             
               
    #col constraints -> up down neiboughounds not equal !!!!!NOT ENTIRE COL
    for j in range(len(variable_array[0])): #in range 10
        colj = [row[j] for row in variable_array]
#        print ("colj",colj)
        #!!!!!sum constraints
        make_sum_cons(colj, last_row[j],constraint_list,j)
#        print("xxxxxx",len(constraint_list))  


        #!!!!all diag and col etc constraints        
        for col in range(num_rows):
            make_adj_cons(constraint_list,num_rows, variable_array,col,j)
#            print("xxxxxx",len(constraint_list))             

##    
    # create csp object
    vars = []
    for row in variable_array:
        for v in row: # ele in each row
            vars.append(v)
            
    tenner_csp = CSP("TENNER-M1", vars)
    for con in constraint_list:
        tenner_csp.add_constraint(con)
    return tenner_csp,variable_array
    # csp consists of variables w/ finite domain, constraints

###    
def make_var_array(cell_rows,n):
    # take in array/puzzle, and number of rows
    var_array = []
    num_ls = [0,1,2,3,4,5,6,7,8,9]
    i = 0
    for row in cell_rows:   #each row
        var_array.append([])
        j = 0
        for cell in row:
            var = Variable("V{},{}".format(i+1,j+1)) # define variables
            var_array[i].append(var)
            if cell == -1:
                var.add_domain_values(num_ls) # domain {0-9}
            else:
                var.add_domain_values([cell])   # domain is existed int
            j+=1
        i+=1
#    print ("var_array:", var_array)
#    print ("var",var)
    return var_array


def process_board(initial_tenner_board):
    n_grid = initial_tenner_board[0]
    # last_row is initially filled which is the sum row
    last_row = initial_tenner_board[1]
#    print ("n_grid", n_grid)
#    print ("last_row:", last_row)
       
    cell_rows = []
    for row in n_grid:
        ind = 0
        c_row = []
        # DO SOMETHING BELOW...
        while ind < len(row):   #len(row)=10
            c_row.append(int(row[ind]))
            ind = ind +1
#        print(c_row)
        cell_rows.append(c_row)
    return cell_rows,last_row



def make_adj_cons(cons_list, n_rows, var_array, x, y):
    i = x
    j = y
    # binary NOT-EQUALS constraint
    coord = [(0,-1),(-1,-1),(-1,0),(-1,1)]
    k = j
    while k > 1:
        coord.append((0,-k))
        k -= 1
    for (m,n) in coord:
        row = i+m
        col = j+n
        # adj
        if (row >= 0 and row <= n_rows) and (col >= 0 and col <= 9):
            # create binary NOT-EQUALS constraint
            # ind for row and column
            var1 = var_array[row][col]
            var2 = var_array[i][j]
            c = Constraint("C({}{}{}{})".format(row,col,i,j), [var1, var2])
            sat_tuples = []
            NE_sat_tuples(var1, var2, sat_tuples)
            c.add_satisfying_tuples(sat_tuples)
            cons_list.append(c)
            
def NE_sat_tuples(var1, var2, sat_tuples):
    for t in itertools.product(var1.domain(), var2.domain()):
        if t[0] != t[1]:
            sat_tuples.append(t)


def make_sum_cons(colj,total,con_list,col):
    c = Constraint("COL{}".format(col), colj)
#    print(c)
    sat_tuples = []
    # get list of all domains
    var_dom_lst = [var.domain() for var in colj]
    # get all possible tuples
    for t in itertools.product(*var_dom_lst):
        if sum(t) == total:
            sat_tuples.append(t)
    c.add_satisfying_tuples(sat_tuples)
    con_list.append(c)


 ###    SOMETHING TO RUN - TEST - DELETE LATER
b1 = ([[-1, 0, 1,-1, 9,-1,-1, 5,-1, 2],
       [-1, 7,-1,-1,-1, 6, 1,-1,-1,-1],
       [-1,-1,-1, 8,-1,-1,-1,-1,-1, 9],
       [ 6,-1, 4,-1,-1,-1,-1, 7,-1,-1],
       [-1, 1,-1, 3,-1,-1, 5, 8, 2,-1]],
      [29,16,18,21,24,24,21,28,17,27])

var_array = make_var_array(b1[0],len(b1[0]))
c_r,lr = process_board(b1) 

###   
    

#tenner_csp, vy = tenner_csp_model_1(b1)


#IMPLEMENT

##############################

def tenner_csp_model_2(initial_tenner_board):
    '''Return a CSP object representing a Tenner Grid CSP problem along 
       with an array of variables for the problem. That is return

       tenner_csp, variable_array

       where tenner_csp is a csp representing tenner using model_1
       and variable_array is a list of lists

       [ [  ]
         [  ]
         .
         .
         .
         [  ] ]

       such that variable_array[i][j] is the Variable (object) that
       you built to represent the value to be placed in cell i,j of
       the Tenner Grid (only including the first n rows, indexed from 
       (0,0) to (n,9)) where n can be 3 to 8.

       The input board takes the same input format (a list of n length-10 lists
       specifying the board as tenner_csp_model_1.
    
       The variables of model_2 are the same as for model_1: a variable
       for each cell of the board, with domain equal to {0-9} if the
       board has a -1 at that position, and domain equal {i} if the board
       has a fixed number i at that cell.

       However, model_2 has different constraints. In particular,
       model_2 has a combination of n-nary 
       all-different constraints and binary not-equal constraints: all-different 
       constraints for the variables in each row, binary constraints for  
       contiguous cells (including diagonally contiguous cells), and n-nary sum 
       constraints for each column. 
       Each n-ary all-different constraint has more than two variables (some of 
       these variables will have a single value in their domain). 
       model_2 should create these all-different constraints between the relevant 
       variables.
    '''

    # process the input to have a board
    cell_rows,last_row = process_board(initial_tenner_board)
    num_rows = len(initial_tenner_board[0]) # n = number of rows, each row with 10 cols
        
    # define variables and add their domain values
    variable_array = make_var_array(cell_rows,num_rows)
    
##    
    # DEFINE CONSTRAINTS:
    # set up the constraints
    constraint_list = []
    #row constraints -> rows 3~8 rows; each row has no duplicates
    # can be computed as ALL-DIFF constraints as in soduko case - bi-nary             
               
    #col constraints -> up down neiboughounds not equal !!!!!NOT ENTIRE COL
    for j in range(len(variable_array[0])): #in range 10
        colj = [row[j] for row in variable_array]
#        print ("colj",colj)
        #!!!!!sum constraints
        make_sum_cons(colj, last_row[j],constraint_list,j)


        #!!!!all diag and col etc constraints        
        for col in range(num_rows):
            make_adj_cons_m2(constraint_list,num_rows, variable_array,col,j)
          

    for row in range(num_rows):
        row_list = []
        for col in range(10):
            row_list.append(variable_array[row][col])
            make_adj_cons_m2(constraint_list,num_rows, variable_array,row,col)
        make_row_cons(row_list, constraint_list, row)

##    
    # create csp object
    vars = []
    for row in variable_array:
        for v in row: # ele in each row
            vars.append(v)
    
    tenner_csp = CSP("TENNER-M2", vars)
    for con in constraint_list:
        tenner_csp.add_constraint(con)
    return tenner_csp,variable_array
    # csp consists of variables w/ finite domain, constraints
    
#IMPLEMENT

def make_row_cons(row_list, cons_list, row):
    c = Constraint("R{}".format(row), row_list)
    sat_tuples = []
    var_dom_list = [var.domain() for var in row_list]
    for t in itertools.product(*var_dom_list):
        # ordering of 10 numbers {0~9} => SUM MUST BE 45
        if sum(t) == 45:
            counts = dict()
            for i in t:
                if counts.get(i, 0) > 0:
                    break
                counts[i] = counts.get(i, 0) + 1
            else:
                sat_tuples.append(t)
    c.add_satisfying_tuples(sat_tuples)
    cons_list.append(c)


def make_adj_cons_m2(cons_list, num_rows, var_array,x,y):
    i = x
    j = y
    # binary NOT-EQUALS constraint
    for (m,n) in [(-1,-1),(-1,0),(-1,1)]:
        row = i+m
        col = j+n
        # adj
        if (row >= 0 and row <= num_rows) and (col >= 0 and col <= 9):
            var1 = var_array[row][col]
            var2 = var_array[i][j]
            c = Constraint("C({}{}{}{})".format(row,col,i,j), [var1, var2])
            sat_tuples = []
            NE_sat_tuples(var1, var2, sat_tuples)
            c.add_satisfying_tuples(sat_tuples)
            cons_list.append(c)
            