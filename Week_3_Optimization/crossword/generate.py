import sys

from crossword import *
import copy

class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        domains = copy.deepcopy(self.domains)
        for variable, words in domains.items():
            for word in words:
                if len(word) != variable.length:
                    self.domains[variable].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        domains = copy.deepcopy(self.domains)
        revision_made = False
        x_cell = -1

        if self.crossword.overlaps.get((x,y), 'NOT_FOUND') != 'NOT_FOUND' and self.crossword.overlaps.get((x,y), 'NOT_FOUND') != None :
            x_cell, y_cell = self.crossword.overlaps.get((x,y)) 
        elif self.crossword.overlaps.get((y, x), 'NOT_FOUND') != 'NOT_FOUND' and self.crossword.overlaps.get((y, x), 'NOT_FOUND') != None:
            y_cell, x_cell = self.crossword.overlaps.get((y, x))

        if x_cell != -1:
            for x_val in domains[x]:
                is_arc_consistent = False
                for y_val in domains[y]:
                    if x_val[x_cell] == y_val[y_cell]:
                        is_arc_consistent = True
                if is_arc_consistent == False:
                    self.domains[x].remove(x_val)
                    revision_made = True
        else:
            return revision_made
        
        return revision_made

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        arcs_overlaps = []
        for x in self.crossword.variables:
            neighbors = self.crossword.neighbors(x)
            for y in neighbors:
                arcs_overlaps.append((x,y))
        
        for x,y in arcs_overlaps:
                revised = self.revise(x, y)
                if revised:
                    if len(self.domains[x]) == 0:
                        return False
                    for neighbor in neighbors:
                        if neighbor is not y:
                            arcs_overlaps.append((neighbor,x))
                    
        for words in self.domains.values():
            if len(words) == 0 :
                return False
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return len(assignment) == len(self.crossword.variables) and len(assignment.values()) == len(assignment)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        if len(set(assignment.values())) != len(assignment.values()):
            return False

        for var, word in assignment.items():
            if var.length != len(word):
                return False
            
            neighbors = self.crossword.neighbors(var)
            for neighbor in neighbors:
                if self.crossword.overlaps.get((var, neighbor), None) != None:
                    x_cell, y_cell = self.crossword.overlaps.get((var, neighbor), None)
                    satisfy_intersection = False
                    if neighbor in assignment:
                        if word != assignment[neighbor][y_cell] and word[x_cell] == assignment[neighbor][y_cell]:
                            satisfy_intersection = True
                    else:
                        for y_val in self.domains[neighbor]:
                            if word != y_val and word[x_cell] == y_val[y_cell]:
                                satisfy_intersection = True
                    if satisfy_intersection != True:
                        return False

                elif self.crossword.overlaps.get((neighbor, var), None) != None:
                    x_cell, y_cell = self.crossword.overlaps.get((var, neighbor), None)
                    satisfy_intersection = False
                    for y_val in self.domains[neighbor]:
                        if word != y_val and word[x_cell] == y_val[y_cell]:
                            satisfy_intersection = True
                    if satisfy_intersection != True:
                        return False
        return True       
        

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        words = self.domains[var]
        neighbors = self.crossword.neighbors(var)
        word_conflicts = {}
        for word in words:
            if word not in word_conflicts:
                word_conflicts[word] = 0        
            for neighbor in neighbors:
                x_cell, y_cell = self.crossword.overlaps.get((var, neighbor), None)
                if neighbor in assignment:
                    if word == assignment[neighbor] or word[x_cell] != assignment[neighbor][y_cell]:
                        word_conflicts[word] += 1
                else:
                    for nei_word in self.domains[neighbor]:
                        if word == nei_word or word[x_cell] != nei_word[y_cell]:
                            word_conflicts[word] += 1

        return {k for k, v in sorted(word_conflicts.items(), key=lambda item: item[1], reverse = True)}
        
        # return self.domains[var]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        min = 1000
        unassigned_var = None
        for var, words in self.domains.items():
            if var not in assignment and len(words) < min:
                unassigned_var = var
                min = len(words)
            
        return unassigned_var

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        while(True):
            if self.assignment_complete(assignment):
                return True
            
            var = self.select_unassigned_variable(assignment)

            for value in self.order_domain_values(var, assignment):
                assignment[var] = value
                if(self.consistent(assignment)):                
                    result = self.backtrack(assignment)
                    if result == True or self.assignment_complete(assignment):
                        break
                else:
                    del assignment[var]

            if self.assignment_complete(assignment): return assignment
            else: return None






def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # structure = r'data\structure2.txt'
    # words = r'data\words2.txt'
    # output = 'output.png'

    # Generate crossword
    # while(True):
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
