import itertools
import random
import copy
import random

class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if(len(self.cells) == self.count):
            return self.cells

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if(self.count == 0):
            return self.cells

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        all_cells = copy.copy(self.cells)
        for eachcell in all_cells:
            if eachcell == cell:
                self.cells.remove(cell)
                self.count -= 1
                

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        all_cells = copy.copy(self.cells)
        for eachcell in all_cells:
            if eachcell == cell:
                self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        #print(f'knowledge count is {len(self.knowledge)}')
        self.moves_made.add(cell)
        MinesweeperAI.mark_safe(self, cell)
        neighbour_cells = MinesweeperAI.getneighbours(self, cell)

        #print(f'1. no of neibours {len(neighbour_cells)}')
        #safe_cells = Sentence.known_safes(neighbour_cells)
        neighbour_cells = [cell for cell in neighbour_cells if cell not in self.safes]
        #print(f'2. no of neibours {len(neighbour_cells)}')
        if(len(neighbour_cells) > 0): self.knowledge.append(Sentence(neighbour_cells, count))
        knwldge = copy.deepcopy(self.knowledge)
        
        for sentence in knwldge:
            subset = False
            new_cells = []
            if(len(neighbour_cells) != 0 and len(sentence.cells) != 0 and sentence.cells != neighbour_cells):
                if(MinesweeperAI.issubset(sentence.cells, neighbour_cells)):
                    subset = True
                    for s_cell in sentence.cells:
                        if s_cell not in neighbour_cells:
                            #print('duh')
                            new_cells.append(s_cell)
                elif(MinesweeperAI.issubset(neighbour_cells, sentence.cells, )):
                    subset = True
                    for s_cell in neighbour_cells:
                        if s_cell not in sentence.cells:
                            #print('duh')
                            new_cells.append(s_cell)
                if(subset):           
                    if(len(new_cells) == 1 and abs(sentence.count - count) == 1):
                        #print(f'Marking {new_cells[0]} as mine')
                        MinesweeperAI.mark_mine(self, new_cells[0])
                    elif(len(new_cells) == 1 and abs(sentence.count - count) == 0):
                        if cell not in self.safes:
                            #print(f'1 Count marking {new_cells[0]} as safe')
                            MinesweeperAI.mark_safe(self, new_cells[0])
                            neighbour_safe_cells = MinesweeperAI.getneighbours(self, new_cells[0])
                            for nei_cell in neighbour_safe_cells:
                                if cell not in self.safes:
                                    #print(f'neigbhour marking {nei_cell} as safe')
                                    MinesweeperAI.mark_safe(self, nei_cell)
                                    #self.safes.add(nei_cell)
                        
                    elif(len(new_cells) != 0):
                        #print(f'adding cells to knowledge {new_cells}')
                        self.knowledge.append(Sentence(new_cells, abs(sentence.count - count)))
                
        #print('hey')
        knwldge = copy.deepcopy(self.knowledge)
        for sentence_new in knwldge:        
            if(sentence_new.count == 0):
                for each_cell in sentence_new.cells:
                    if each_cell not in self.safes:
                        #print(f'fail{cell}')
                        #print(f'Final marking {cell} as safe')
                        MinesweeperAI.mark_safe(self, each_cell)
            if(len(sentence_new.cells) > 0 and sentence_new.count == len(sentence_new.cells)):
                #print(sentence_new.cells)
                #print('hey')
                for each_cell in sentence_new.cells:
                    #print(f'Marking {cell} as mine')
                    MinesweeperAI.mark_mine(self, each_cell)
            
        #print('knwldge done')
        fin_knwldge = self.knowledge
        
        for ech_sent  in fin_knwldge:
            if len(ech_sent.cells) == 0:
                #print('dropping empty sentence')
                self.knowledge.remove(ech_sent)
        
    def getneighbours(self, cell):
        neighbour_cells = []
        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
    
                # Ignore the cell itself
                if (i, j) == cell:
                    continue
                if 0 <= i < self.height and 0 <= j < self.width:
                    neighbour_cells.append((i,j))
        
        return neighbour_cells


    def issubset(superset,subset):
        return all(item in superset for item in subset)
    
    def madewrongmove(self, cell):
        #print(f'You chose {cell}')
        #print(f'marked mines are')
        # for eachsafecell in self.mines:
        #     print(eachsafecell)
        if(cell in self.safes): print('Wrong move is part of safe moves..!')
        
    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if cell not in self.moves_made and cell not in self.mines:
                #print(f'safe move is\t{cell}')
                return cell
        
        # for sent_know in self.knowledge:
        #     Sentence.known_safes(sent_know)
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        
        if(len(self.moves_made) <= 2):
            while(True):
                i = random.randint(0, 7)
                j = random.randint(0, 7)
                if((i, j) not in self.moves_made):
                    return (i,j)
                
        for i in range(0, 8):
            for j in range(0, 8):

                # Ignore the cell itself
                if (i, j) not in self.moves_made and (i,j) not in self.mines:
                    #print(f'random move is\t{(i,j)}')
                    return (i,j) 
        #print(f'rand func, {self.moves_made}')
