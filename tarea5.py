import csv
import graphviz
import os

# con esta clase estaremos guardando las llaves y las hojas de nuestro arbol
class BTreeNode:
    def __init__(self, leaf=False):
        self.leaf = leaf
        self.keys = []
        self.child = []

# se solicitara que se añada el grado del arbol
class BTree:
    def __init__(self, t):
        self.root = BTreeNode(True)
        # 't' es el grado del Árbol B
        self.t = t
#la clase print_tree analisa que grado del arbol es
    def print_tree(self, x, l=0):
        print("Nivel ", l, " ", len(x.keys), end=":")
        for i in x.keys:
            print(i, end=" ")
        print()
        l += 1
        if len(x.child) > 0:
            for i in x.child:
                self.print_tree(i, l)

#la clase Search lo que genera es una busqueda por medio del arbol desde la raiz 
    def search(self, k, x=None):
        """Busca la clave 'k' a partir de la posición 'x'.
        Si 'x' no se especifica, la búsqueda comienza desde la raíz.

        Retorna 'None' si 'k' no se encuentra.
        En caso contrario, retorna una tupla con el nodo y el índice donde se encontró la clave.

        Argumentos:
            k -- clave a buscar
            x -- posición desde donde buscar
        """
        if x is None:
            # Buscar en todo el árbol si no se proporciona un nodo
            return self.search(k, self.root)
        
        i = 0
        while i < len(x.keys) and k > x.keys[i]:
            i += 1
            
        if i < len(x.keys) and k == x.keys[i]:
            return (x, i)
        elif x.leaf:
            return None
        else:
            # Buscar en los hijos
            return self.search(k, x.child[i])
        
#la clase insert, añade un nuevo hijo, hoja o raiz y los junta como un arbol B
    def insert(self, k):
        """Llama a funciones auxiliares para insertar la clave 'k' en el Árbol B

        Argumentos:
            k -- clave a insertar
        """
        root = self.root
        # Si la raíz está llena, debemos dividirla
        if len(root.keys) == (2 * self.t) - 1:
            temp = BTreeNode()
            self.root = temp
            # La antigua raíz se convierte en el primer hijo de la nueva raíz 'temp'
            temp.child.insert(0, root)
            self._split_child(temp, 0)
            self._insert_nonfull(temp, k)
        else:
            self._insert_nonfull(root, k)

    def _insert_nonfull(self, x, k):
        """Inserta la clave 'k' en la posición 'x' en un nodo no lleno

        Argumentos:
            x -- Posición del nodo
            k -- clave a insertar
        """
        i = len(x.keys) - 1
        if x.leaf:
            x.keys.append(None)
            while i >= 0 and k < x.keys[i]:
                x.keys[i + 1] = x.keys[i]
                i -= 1
            x.keys[i + 1] = k
        else:
            while i >= 0 and k < x.keys[i]:
                i -= 1
            i += 1
            if len(x.child[i].keys) == (2 * self.t) - 1:
                self._split_child(x, i)
                if k > x.keys[i]:
                    i += 1
            self._insert_nonfull(x.child[i], k)

    def _split_child(self, x, i):
        """Divide el hijo del nodo en 'x' desde el índice 'i'

        Argumentos:
            x -- nodo padre del nodo a dividir
            i -- valor del índice del hijo
        """
        t = self.t
        y = x.child[i]
        z = BTreeNode(y.leaf)
        x.child.insert(i + 1, z)
        x.keys.insert(i, y.keys[t - 1])
        z.keys = y.keys[t: (2 * t) - 1]
        y.keys = y.keys[0: t - 1]
        if not y.leaf:
            z.child = y.child[t: 2 * t]
            y.child = y.child[0: t]

#Delete recorre todo el arbol y a travez de la busqueda elimina.
    def delete(self, x, k):
        """Llama a funciones auxiliares para eliminar la clave 'k' después de buscar desde el nodo 'x'

        Argumentos:
            x -- nodo, según cuya posición relativa, se llaman las funciones auxiliares
            k -- clave a eliminar
        """
        t = self.t
        i = 0
        while i < len(x.keys) and k > x.keys[i]:
            i += 1
        # Eliminar la clave si el nodo es una hoja
        if x.leaf:
            if i < len(x.keys) and k == x.keys[i]:
                x.keys.pop(i)
                return
            return

        # Llamar a '_delete_internal_node' cuando x es un nodo interno y contiene la clave 'k'
        if i < len(x.keys) and k == x.keys[i]:
            return self._delete_internal_node(x, k, i)
        # Llamar recursivamente a 'delete' en el hijo de x
        elif len(x.child[i].keys) >= t:
            self.delete(x.child[i], k)
        # Asegurar que un hijo siempre tenga al menos 't' claves
        else:
            if i != 0 and i + 2 < len(x.child):
                if len(x.child[i - 1].keys) >= t:
                    self._delete_sibling(x, i, i - 1)
                elif len(x.child[i + 1].keys) >= t:
                    self._delete_sibling(x, i, i + 1)
                else:
                    self._del_merge(x, i, i + 1)
            elif i == 0:
                if len(x.child[i + 1].keys) >= t:
                    self._delete_sibling(x, i, i + 1)
                else:
                    self._del_merge(x, i, i + 1)
            elif i + 1 == len(x.child):
                if len(x.child[i - 1].keys) >= t:
                    self._delete_sibling(x, i, i - 1)
                else:
                    self._del_merge(x, i, i - 1)
            self.delete(x.child[i], k)

    def _delete_internal_node(self, x, k, i):
        """Elimina nodo interno

        Argumentos:
            x -- nodo interno en el que está presente la clave 'k'
            k -- clave a eliminar
            i -- posición del índice de la clave en la lista
        """
        t = self.t
        # Eliminar la clave si el nodo es una hoja
        if x.leaf:
            if k == x.keys[i]:
                x.keys.pop(i)
                return
            return

        # Reemplazar la clave con su predecesor y eliminar el predecesor
        if len(x.child[i].keys) >= t:
            x.keys[i] = self._delete_predecessor(x.child[i])
            return
        # Reemplazar la clave con su sucesor y eliminar el sucesor
        elif len(x.child[i + 1].keys) >= t:
            x.keys[i] = self._delete_successor(x.child[i + 1])
            return
        # Fusionar el hijo, su hermano izquierdo y la clave 'k'
        else:
            self._del_merge(x, i, i + 1)
            self._delete_internal_node(x.child[i], k, self.t - 1)

    def _delete_predecessor(self, x):
        """Retorna y elimina el predecesor de la clave 'k' que se va a eliminar

        Argumentos:
            x -- nodo
        """
        if x.leaf:
            return x.keys.pop()
        n = len(x.keys) - 1
        if len(x.child[n].keys) >= self.t:
            self._delete_sibling(x, n + 1, n)
        else:
            self._del_merge(x, n, n + 1)
        self._delete_predecessor(x.child[n])

    def _delete_successor(self, x):
        """Retorna y elimina el sucesor de la clave 'k' que se va a eliminar

        Argumentos:
            x -- nodo
        """
        if x.leaf:
            return x.keys.pop(0)
        if len(x.child[1].keys) >= self.t:
            self._delete_sibling(x, 0, 1)
        else:
            self._del_merge(x, 0, 1)
        self._delete_successor(x.child[0])

    def _del_merge(self, x, i, j):
        """Fusiona los hijos de x y una de sus propias claves

        Argumentos:
            x -- nodo padre
            i -- índice de uno de los hijos
            j -- índice de uno de los hijos
        """
        cnode = x.child[i]

        # Fusionar x.child[i], x.child[j] y x.keys[i]
        if j > i:
            rsnode = x.child[j]
            cnode.keys.append(x.keys[i])
            # Asignar claves del nodo hermano derecho al nodo hijo
            for k in range(len(rsnode.keys)):
                cnode.keys.append(rsnode.keys[k])
                if len(rsnode.child) > 0:
                    cnode.child.append(rsnode.child[k])
            if len(rsnode.child) > 0:
                cnode.child.append(rsnode.child.pop())
            new = cnode
            x.keys.pop(i)
            x.child.pop(j)
        # Fusionar x.child[i], x.child[j] y x.keys[j]
        else:
            lsnode = x.child[j]
            lsnode.keys.append(x.keys[j])
            # Asignar claves del nodo hermano izquierdo al nodo hijo
            for i in range(len(cnode.keys)):
                lsnode.keys.append(cnode.keys[i])
                if len(lsnode.child) > 0:
                    lsnode.child.append(cnode.child[i])
            if len(lsnode.child) > 0:
                lsnode.child.append(cnode.child.pop())
            new = lsnode
            x.keys.pop(j)
            x.child.pop(i)

        # Si x es la raíz y está vacía, reasignar la raíz
        if x == self.root and len(x.keys) == 0:
            self.root = new

    def _delete_sibling(self, x, i, j):
        """Toma prestada una clave del j-ésimo hijo de x y la agrega al i-ésimo hijo de x

        Argumentos:
            x -- nodo padre
            i -- índice de uno de los hijos
            j -- índice de uno de los hijos
        """
        cnode = x.child[i]
        if i < j:
            # Tomar prestada clave del hermano derecho del hijo
            rsnode = x.child[j]
            cnode.keys.append(x.keys[i])
            x.keys[i] = rsnode.keys[0]
            if len(rsnode.child) > 0:
                cnode.child.append(rsnode.child[0])
                rsnode.child.pop(0)
            rsnode.keys.pop(0)
        else:
            # Tomar prestada clave del hermano izquierdo del hijo
            lsnode = x.child[j]
            cnode.keys.insert(0, x.keys[i - 1])
            x.keys[i - 1] = lsnode.keys.pop()
            if len(lsnode.child) > 0:
                cnode.child.insert(0, lsnode.child.pop())

#Genera la grafica del arbol posicionandolo como un arbol B y su estructura. A travez de Graphiz
    def visualize(self, filename="btree"):
        """Genera una representación visual del árbol usando Graphviz

        Argumentos:
            filename -- nombre del archivo de salida (sin extensión)
        """
        dot = graphviz.Digraph(comment='B-Tree')
        
        def add_nodes_edges(node, node_id):
            # Crear el nodo con sus claves
            label = "|".join([str(key) for key in node.keys])
            dot.node(str(node_id), f"{{{label}}}")
            
            # Si no es hoja, agregar los hijos
            if not node.leaf:
                for i, child in enumerate(node.child):
                    child_id = f"{node_id}_{i}"
                    add_nodes_edges(child, child_id)
                    dot.edge(str(node_id), child_id)
        
        # Comenzar con la raíz
        add_nodes_edges(self.root, "root")
        
        # Renderizar el gráfico
        dot.render(filename, format='png', cleanup=True)
        print(f"Árbol visualizado y guardado como {filename}.png")

#cargar datos unicamente desde un archivo CSV que lo busca a travez del explorador de archivos
    def load_from_csv(self, filename):
        """Carga datos desde un archivo CSV

        Argumentos:
            filename -- ruta al archivo CSV
        """
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row:  # Si la fila no está vacía
                        try:
                            # Intentar convertir a entero
                            key = int(row[0])
                            self.insert(key)
                        except ValueError:
                            # Si no es un entero, usar como string
                            self.insert(row[0])
            print(f"Datos cargados exitosamente desde {filename}")
        except FileNotFoundError:
            print(f"Error: El archivo {filename} no fue encontrado.")
        except Exception as e:
            print(f"Error al cargar datos: {e}")

def clear_screen():
    """Limpia la pantalla de la consola"""
    os.system('cls' if os.name == 'nt' else 'clear')

#El menu principal con las opciónes solicitadas.
def main():
    clear_screen()
    print("=== PROGRAMA DE ÁRBOL B ===")
    
    # Configuración inicial
    while True:
        try:
            t = int(input("\nIngrese el grado del Árbol B: "))
            if t < 2:
                print("El grado debe ser al menos 2.")
            else:
                break
        except ValueError:
            print("Por favor, ingrese un número entero válido.")
    
    # Crear árbol B
    btree = BTree(t)
    
    while True:
        clear_screen()
        print("\n=== PROGRAMA DE ÁRBOL B ===")
        print(f"Grado actual: {t}")
        print("\n1. Insertar clave")
        print("2. Buscar clave")
        print("3. Eliminar clave")
        print("4. Cargar datos desde archivo CSV")
        print("5. Visualizar árbol")
        print("6. Mostrar árbol en consola")
        print("7. Salir")
        
        choice = input("\nElija una opción (1-7): ")
        
        if choice == '1':
            try:
                key_str = input("\nIngrese la clave a insertar: ")
                try:
                    key = int(key_str)
                except ValueError:
                    key = key_str
                
                btree.insert(key)
                print(f"\nClave {key} insertada correctamente.")
            except Exception as e:
                print(f"\nError al insertar: {e}")
            input("\nPresione Enter para continuar...")
            
        elif choice == '2':
            try:
                key_str = input("\nIngrese la clave a buscar: ")
                try:
                    key = int(key_str)
                except ValueError:
                    key = key_str
                
                result = btree.search(key)
                if result:
                    print(f"\nClave {key} encontrada en el árbol.")
                else:
                    print("\nClave no encontrada.")
            except Exception as e:
                print(f"\nError al buscar: {e}")
            input("\nPresione Enter para continuar...")
            
        elif choice == '3':
            try:
                key_str = input("\nIngrese la clave a eliminar: ")
                try:
                    key = int(key_str)
                except ValueError:
                    key = key_str
                
                if btree.search(key):
                    btree.delete(btree.root, key)
                    print(f"\nClave {key} eliminada correctamente.")
                else:
                    print("\nClave no encontrada.")
            except Exception as e:
                print(f"\nError al eliminar: {e}")
            input("\nPresione Enter para continuar...")
            
        elif choice == '4':
            try:
                filename = input("\nIngrese la ruta del archivo CSV: ")
                btree.load_from_csv(filename)
            except Exception as e:
                print(f"\nError al cargar el archivo: {e}")
            input("\nPresione Enter para continuar...")
            
        elif choice == '5':
            try:
                filename = input("\nIngrese el nombre del archivo de salida (sin extensión): ") or "btree"
                btree.visualize(filename)
                print(f"\nÁrbol visualizado y guardado como {filename}.png")
            except Exception as e:
                print(f"\nError al visualizar: {e}")
                print("Asegúrese de tener instalado Graphviz y que esté en la ruta del sistema.")
                print("Puede instalarlo con: pip install graphviz")
                print("Y luego instalar el paquete Graphviz desde: https://graphviz.org/download/")
            input("\nPresione Enter para continuar...")
            
        elif choice == '6':
            clear_screen()
            print("\n=== ÁRBOL B EN CONSOLA ===")
            btree.print_tree(btree.root)
            input("\nPresione Enter para continuar...")
            
        elif choice == '7':
            print("\n¡Gracias por usar el programa de Árbol B!")
            break
            
        else:
            print("\nOpción no válida. Por favor, elija una opción del 1 al 7.")
            input("\nPresione Enter para continuar...")

if __name__ == '__main__':
    main()