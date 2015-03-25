#Ivo Silva, 64833
#Ricardo Martins, 64401

# Modulo: tree_search
# 
# Fornece um conjunto de classes para suporte a resolucao de 
# problemas por pesquisa em arvore:
#    SearchDomain  - dominios de problemas
#    SearchProblem - problemas concretos a resolver 
#    SearchNode    - nos da arvore de pesquisa
#    SearchTree    - arvore de pesquisa, com metodos para 
#                    a respectiva construcao

# Dominios de pesquisa
# Permitem calcular
# as accoes possiveis em cada estado, etc
class SearchDomain:
    # construtor
    def __init__(self):
        abstract
    # lista de accoes possiveis num estado
    def actions(self, state):
        abstract
    # resultado de uma accao num estado, ou seja, o estado seguinte
    def result(self, state, action):
        abstract
    # custo de uma accao num estado
    def cost(self, state, action):
        abstract
    # custo estimado de chegar de um estado a outro
    def heuristic(self, state, goal_state):
        abstract

# Problemas concretos a resolver
# dentro de um determinado dominio
class SearchProblem:
    def __init__(self, domain, initial, goal):
        self.domain = domain
        self.initial = initial
        self.goal = goal
    def goal_test(self, state):
        return str(state) == str(self.goal)

# Nos de uma arvore de pesquisa
class SearchNode:
    def __init__(self,state,parent,cost): 
        self.state = state
        self.parent = parent
        self.cost = cost

# Arvores de pesquisa
class SearchTree:

    # construtor
    def __init__(self,problem, strategy='breadth', limit = None): 
        self.problem = problem
        root = SearchNode(problem.initial, None,0)
        self.open_nodes = [root]
        self.strategy = strategy

    # obter o caminho (sequencia de estados) da raiz ate um no
    def get_path(self,node):
        if node.parent == None:
            return [node.state]
        path = self.get_path(node.parent)
        path += [node.state]
        return(path)

    # procurar a solucao
    def search(self):
        while True:
            if self.open_nodes == []:
                return None
            node = self.open_nodes[0]
            if self.problem.goal_test(str(node.state)):
                #print "getPath",self.get_path(node)
                return (self.get_path(node))
            self.open_nodes[0:1] = []
            actions = self.problem.domain.actions(str(node.state))
            lnewnodes = []
            for a in actions:
                newstate = self.problem.domain.result(str(node.state),a)
                if newstate not in self.get_path(node):
                    newnode = SearchNode(str(newstate),node,node.cost + 1)
                    lnewnodes += [newnode]
            self.add_to_open(lnewnodes)

    # juntar novos nos a lista de nos abertos de acordo com a estrategia
    def add_to_open(self,lnewnodes):
        if self.strategy == 'breadth':
            self.open_nodes.extend(lnewnodes)
        elif self.strategy == 'depth':
            self.open_nodes[0:0] = lnewnodes
        elif self.strategy == 'uniform':
            self.open_nodes.extend(lnewnodes)
            self.open_nodes.sort(key = lambda node : node.cost)
        
