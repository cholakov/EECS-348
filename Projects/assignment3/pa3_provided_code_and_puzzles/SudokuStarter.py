import struct, string, math
from copy import *
from operator import itemgetter

    
# EECS 348 Problem Set 3
# Contributors:  Joseph Lee, Vesko Cholakov
# 


# ---------- Starter Code ----------------

class SudokuBoard:
    """This will be the sudoku board game object your player will manipulate."""
 
    def __init__(self, size, board):
      """the constructor for the SudokuBoard"""
      self.BoardSize = size #the size of the board
      self.CurrentGameBoard= board #the current state of the game board

    def set_value(self, row, col, value):
        """This function will create a new sudoku board object with the input
       value placed on the GameBoard row and col are both zero-indexed"""
        #add the value to the appropriate position on the board
        self.CurrentGameBoard[row][col]=value
        self.update_domain(row,col,value)
        #return a new board of the same size with the value added
        return SudokuBoard(self.BoardSize, self.CurrentGameBoard)
                                                                 
                                                         
    def print_board(self):
        """Prints the current game board. Leaves empty_space spots blank."""
        div = int(math.sqrt(self.BoardSize))
        dash = ""
        space = ""
        line = "+"
        sep = "|"
        for ii in range(div):
            dash += "----"
            space += "    "
        for ii in range(div):
            line += dash + "+"
            sep += space + "|"
        for ii in range(-1, self.BoardSize):
            if ii != -1:
                print "|",
                for jj in range(self.BoardSize):
                    if self.CurrentGameBoard[ii][jj] > 9:
                        print self.CurrentGameBoard[ii][jj],
                    elif self.CurrentGameBoard[ii][jj] > 0:
                        print "", self.CurrentGameBoard[ii][jj],
                    else:
                        print "  ",
                    if (jj+1 != self.BoardSize):
                        if ((jj+1)//div != jj/div):
                            print "|",
                        else:
                            print "",
                    else:
                        print "|"
            if ((ii+1)//div != ii/div):
                print line
            else:
                print sep

def parse_file(filename):
    """Parses a sudoku text file into a BoardSize, and a 2d array which holds
   the value of each blank_space. Array elements holding a 0 are considered to be
   empty."""
 
    f = open(filename, 'r')
    BoardSize = int( f.readline())
    NumVals = int(f.readline())
 
    #initialize a blank board
    board= [ [ 0 for ii in range(BoardSize) ] for jj in range(BoardSize) ]
 
    #populate the board with initial values
    for ii in range(NumVals):
        line = f.readline()
        chars = line.split()
        row = int(chars[0])
        col = int(chars[1])
        val = int(chars[2])
        board[row-1][col-1]=val
   
    return board


   
def is_complete(sudoku_board):
    """Takes in a sudoku board and tests to see if it has been filled in
   correctly."""
    b_array = sudoku_board.CurrentGameBoard
    size = len(b_array)
    subsquare = int(math.sqrt(size))
 
    #check each blank_space on the board for a 0, or if the value of the blank_space
    #is present elsewhere within the same row, column, or square
    for row in range(size):
        for col in range(size):
            if b_array[row][col]==0:
                return False
            for ii in range(size):
                if ((b_array[row][ii] == b_array[row][col]) and ii != col):
                    return False
                if ((b_array[ii][col] == b_array[row][col]) and ii != row):
                    return False
            #determine which square the blank_space is in
            sq_row = row // subsquare
            sq_col = col // subsquare
            for ii in range(subsquare):
                for jj in range(subsquare):
                    if((b_array[sq_row*subsquare+ii][sq_col*subsquare+jj]
                            == b_array[row][col])
                        and (sq_row*subsquare + ii != row)
                        and (sq_col*subsquare + jj != col)):
                            return False
    return True


def init_board(file_name):
    """Creates a SudokuBoard object initialized with values from a text file"""
    board = parse_file(file_name)
    return SudokuDomain(len(board), board) # Changed class to SudokuDomain to use child methods
 




# ----------- SudokuDomain Class --------------                

class SudokuDomain(SudokuBoard):
    """Child class from SudokuBoard that includes additional methods for domain-based
    processing. """

    def __init__(self, size, board):
        self.BoardSize = size #the size of the board
        self.CurrentGameBoard= board #the current state of the game board
        self.Domains = self.my_domains() #the current state of the my_domains of gameboard

    def empty_domains(self):
        """Returns predicate results fr empty list/domains"""

        my_domains=self.Domains
        s1 = self.BoardSize

        for row in range(s1):
            for col in range(s1):
                if(my_domains[row][col]==[]):
                    return True
        return False

    def set_value(self, row, col, value):
        """This function will create a new sudoku board object with the input
       value placed on the GameBoard row and col are both zero-indexed"""
        #add the value to the appropriate position on the board
        self.CurrentGameBoard[row][col]=value
        self.update_domain(row,col,value)
        #return a new board of the same size with the value added
        return SudokuDomain(self.BoardSize, self.CurrentGameBoard)

    def count_domains(self):
        """Return Domain count"""
        my_domains=self.Domains
        size = self.BoardSize
        cc = 0
        for row in range(size):
            for col in range(size):
                cc+=1

        return (math.sqrt(int(cc)))


    def get_all_empty(self):
        """Returns a list of the row and col of empty variables or domain cells"""
        ec_list=[]

        for row in range(self.BoardSize):
            for col in range(self.BoardSize):
                if(self.CurrentGameBoard[row][col] == 0):
                    ec_list.append([row, col])
        return ec_list

    def filter_domain(self):
        """Strips zeros from domains"""

        my_domains = self.Domains
        for row in range(self.BoardSize):
            for col in range(self.BoardSize):
                if(isinstance(my_domains[row][col],list)):
                    if 0 in my_domains[row][col]: my_domains[row][col].remove(0)    
        self.Domains = my_domains



    def find_rem_values(self):
        """ find values with lowest domain, preprocessing methods"""

        dc_list=[]
        len_list=[]
        rem_dict = {}
        ec = self.get_all_empty()
        for integer in range(0,len(ec)):
            temp = ec[integer]
            len_list.append(len(self.find_domain(temp[0],temp[1])))
        rem_dict = zip(len_list,ec)
        sorted_remain = sorted(rem_dict, key = itemgetter(0))
        unzip_remain = zip(*sorted_remain)
        ec_sort = unzip_remain[1]

        for integer in range(0,len(ec_sort)):
            dc_list.append(ec_sort[integer])

        return dc_list[::-1]

 
    def find_domain(self, row, col):
        """Returns Domain of a single variable or cell in domain"""
        b_array = self.CurrentGameBoard
        init_dom = []
        if (b_array[row][col] != 0):
            curr_dom = [(b_array[row][col])]
        else:

            for ii in range(1, self.BoardSize+1):
                init_dom.append(ii) 

            temp = init_dom
            for c in range(0, self.BoardSize):
                if (b_array[row][c] != 0):
                    temp[(b_array[row][c])-1] = 0

            for r in range(0, self.BoardSize):
                if (b_array[r][col] != 0 ):
                    temp[(b_array[r][col])-1] = 0
 
            subsquare = int(math.sqrt(self.BoardSize))
            sq_row = row // subsquare
            sq_col = col // subsquare
            for ii in range(subsquare):
                for jj in range(subsquare):
                   if(b_array[sq_row*subsquare+ii][sq_col*subsquare+jj]!=0):
                        temp[(b_array[sq_row*subsquare+ii][sq_col*subsquare+jj]) - 1] = 0
 
            for val in range(1, self.BoardSize):
                if (temp[self.BoardSize-val] == 0):
                    curr_dom = temp
                    curr_dom.pop(self.BoardSize-val)
        return curr_dom

    def my_domains(self):
        """Generates an array of arrays formatted to current game board"""
        my_domains = []
        temp = deepcopy(self.CurrentGameBoard)

        list = self.get_all_empty()
        for blank_space in list:
            my_domains.append(self.find_domain(blank_space[0],blank_space[1]))
            temp[blank_space[0]][blank_space[1]]= self.find_domain(blank_space[0],blank_space[1])
        return temp
 

    def update_domain(self,row,col,val):
        """Updates domain of current game board.  """
        my_domains = self.Domains
        submath = math.sqrt(self.BoardSize)
 
        for c in range(0, self.BoardSize):
            if(isinstance(my_domains[row][c],list)):
                if val in my_domains[row][c]: 
                    my_domains[row][c].remove(val)
 
        for r in range(0, self.BoardSize):
            if(isinstance(my_domains[r][col],list)):
                if val in my_domains[r][col]: 
                    my_domains[r][col].remove(val)
 
        subsquare = int(submath)
        sq_row = row // subsquare
        sq_col = col // subsquare
        for ii in range(subsquare):
            for jj in range(subsquare):
                if(isinstance(my_domains[sq_row*subsquare+ii][sq_col*subsquare+jj],list)):
                   if val in my_domains[sq_row*subsquare+ii][sq_col*subsquare+jj]: 
                    my_domains[sq_row*subsquare+ii][sq_col*subsquare+jj].remove(val)
        self.Domains=my_domains   




# ----------- Non-Class Functions --------------
 
 
def is_consistent(sudoku_board):
    """Takes in a sudoku board and tests to see if it is legal"""
    b_array = sudoku_board.CurrentGameBoard
    size = len(b_array)
    subsquare = int(math.sqrt(size))
    #check if each value
    #is present elsewhere within the same row, column, or square
    for row in range(size):
        for col in range(size):
            for ii in range(size):
                if ((b_array[row][ii] == b_array[row][col]) and (b_array[row][ii]!=0) and (ii != col)):
                    return False
                if ((b_array[ii][col] == b_array[row][col]) and (b_array[ii][col]!=0) and (ii != row)):
                    return False
            #determine which square the blank_space is in
            sq_row = row // subsquare
            sq_col = col // subsquare
            for ii in range(subsquare):
                for jj in range(subsquare):
                    if((b_array[sq_row*subsquare+ii][sq_col*subsquare+jj]
                            == b_array[row][col])
                        and (sq_row*subsquare + ii != row)
                        and (sq_col*subsquare + jj != col)
                        and (b_array[sq_row*subsquare+ii][sq_col*subsquare+jj]!=0)):  #Based off of is_complete
                            return False
    return True

 
 
def Backtracking(sudoku_board,forward_checking, MRV, MCV,LCV):
    """
    Performs backtracking search.
    Follows no particular order.  


    """

    global consistency_counter

    r_index = 0 
    c_index = 1

    if(is_complete(sudoku_board)):
        print "Backtrackinging complete..."
        return sudoku_board
   
    empty_space = sudoku_board.get_all_empty()
    current_cell= empty_space.pop()
    x_domain = range(1,sudoku_board.BoardSize+1)
    for v in x_domain:
        consistency_counter+=1
        temp=deepcopy(sudoku_board.set_value(current_cell[r_index],current_cell[c_index],v))
        if(is_consistent(temp)):

            temp.set_value(current_cell[r_index],current_cell[c_index],v)
            result = Backtracking(temp,forward_checking, MRV, MCV,LCV)
            if (result != False):
                return result

    return False
                 
 
def forward_check(sudoku_board, forward_checking, MRV, MCV, LCV):
    """
    Performs forward check searching.

    """

    r_index = 0
    c_index = 1
    global consistency_counter
    if(is_complete(sudoku_board)):
        print "forward check finished..."
        return sudoku_board
 

    empty_space = sudoku_board.get_all_empty()

    # Determines which method/heuristic/ordering to use.  
   
    if(MRV):
        current_cell = Lowest_Domains(sudoku_board,empty_space) #mrv
    elif(MCV):
        current_cell = Highest_Degree(sudoku_board,empty_space) #mcv
    else:
        current_cell = empty_space.pop()

    if(is_complete(sudoku_board)):
        return sudoku_board

    x_domain = sudoku_board.Domains[current_cell[r_index]][current_cell[c_index]]

    if (LCV):
        x_domain = Least_Constraining(sudoku_board, current_cell[r_index], current_cell[c_index], x_domain)


    #for each value v in x_domain do
    for v in range(len(x_domain)):
        v = x_domain[v]
        consistency_counter+=1

        x_domain = deepcopy(x_domain)
        temp = deepcopy(sudoku_board.set_value(current_cell[0],current_cell[1],v))
        temp.filter_domain()
        if (temp.empty_domains()):
            continue
        if(is_consistent(temp)):
 
            #add (X=v) to a
            temp.set_value(current_cell[0],current_cell[1],v)
            #result <- CPS-Backtracking
            result = forward_check(temp,forward_checking, MRV, MCV,LCV)
            #if result != failure then return
            if (result != False):
                return result 
    return False


def Lowest_Domains(sudoku_board,domain_list):
    """
    Returns variable with smallest domain or legal moves

    """

    r = 0
    c = 1
    min = sudoku_board.BoardSize
    if (domain_list ==[]):
        return 0
    for blank_space in domain_list:
        if(len(sudoku_board.Domains[blank_space[r]][blank_space[c]]) < min):
            min =len(sudoku_board.Domains[blank_space[r]][blank_space[c]])
            min_val=blank_space
    return min_val 

def Highest_Degree(sudoku_board,domain_list):
    """
    Returns variable with greatest degree.

    """
    r_index = 0
    c_index = 1
    max=-1
    t_list=[]
    b_array = sudoku_board.CurrentGameBoard
    size = len(b_array)
    submath = math.sqrt(size)
    subsquare = int(submath)
    for blank_space in domain_list:
        #check the row col and grid of the blank_space to see how many empty spaces remain
        for row in range(size):
            ##same col
            if ((not row == blank_space[r_index]) and (b_array[row][blank_space[c_index]]==0)):
               if [row,blank_space[c_index]] not in t_list: t_list.append([row,blank_space[c_index]])
 
        for col in range(size):            
             ##same row
             if ((not col == blank_space[c_index]) and (b_array[blank_space[r_index]][col]==0)):
                if [blank_space[r_index],col]   not in t_list: t_list.append([blank_space[r_index],col])
     
        sq_row = blank_space[r_index] // subsquare
        sq_col = blank_space[c_index] // subsquare

        for ii in range(subsquare):
            for jj in range(subsquare):
                if((not(sq_row*subsquare+ii ==blank_space[r_index] and sq_col*subsquare+jj==blank_space[c_index])) and b_array[sq_row*subsquare+ii][sq_col*subsquare+jj]==0):
                        if [[sq_row*subsquare+ii],[sq_col*subsquare+jj]] not in t_list: 
                            t_list.append([sq_row*subsquare+ii,sq_col*subsquare+jj])

        t_max=0
        t_max=len([list(x) for x in set(tuple(x) for x in t_list)])

        if(t_max>max):
            max = t_max
            deg_return=blank_space
        t_list=[]
    return deg_return


def Least_Constraining(sudoku_board, row, column, domain):
    """ Orders the values in the domain in ascending order. 
    The first value rules out fewer choices for other empty_space variables than the second value does, and so forth.
    Returns an array of domain values ordered in ascending order. """

    if len(domain) == 1:
        return domain

    constraining_factor = {}
    b_array = sudoku_board.CurrentGameBoard
    size = len(b_array)
    subsquare = int(math.sqrt(size))

    for value in domain:
        appears = 0
        # Find how many times value appears in the domain of cells in the same -- column --
        for row in range(sudoku_board.BoardSize):
            cell_domain = sudoku_board.find_domain(row, column)
            for item in cell_domain:
                if item == value:
                    appears += 1

        # Find how many times value appears in the domain of cells in the same -- row --
        for column in range(sudoku_board.BoardSize):
            cell_domain = sudoku_board.find_domain(row, column)
            for item in cell_domain:
                if item == value:
                    appears += 1   

        
        # Find how many times value appears in the domain of cells in the same -- subsquare --
        sq_row = row // subsquare
        sq_col = column // subsquare

        for ii in range(subsquare):
            for jj in range(subsquare):
                r = (sq_row * subsquare) + ii
                c = (sq_col * subsquare) + jj
                # Exclude cells in the same row or column (we've already examined them)
                if (r != row and c != column):
                    cell_domain = sudoku_board.find_domain(r, c)
                    for item in cell_domain:
                        if item == value:
                            appears += 1 

        constraining_factor[value] = appears

    return sorted(constraining_factor, key = constraining_factor.get)
 
    #for value in x_domain:

    # for each value in the domain
        # count how many times the value appear in the same column, row and subsquare
        # order the values in ascending order



def solve(initial_board, forward_checking = False, MRV = False, MCV = False,LCV = False):
    """
    Modified solve function to act as wrapper for sudoku solving heuristics.


    """
    if (forward_checking):
        return forward_check(initial_board,forward_checking,MRV,MCV,LCV)
    else:
        return Backtracking(initial_board, forward_checking, MRV,MCV,LCV)



def main():

    # Consistency check counter
    global consistency_counter
    consistency_counter=0

    # Weird thing: for /more/9x9/9x9.19, LCV worsens performance

    #sb = init_board("input_puzzles/more/16x16/16x16.18.sudoku")
    #sb = init_board("input_puzzles/more/9x9/9x9.18.sudoku") # <-- particularly difficult
    #sb = init_board("input_puzzles/easy/16_16.sudoku")

    #sb.print_board()
    #sb_solved=solve(sb, True, False, True, False)
    #sb_solved.print_board()

    #sb_solved.print_board()   
    #print "Consistency: " + str(consistency_counter)




if __name__ == "__main__":
    main()