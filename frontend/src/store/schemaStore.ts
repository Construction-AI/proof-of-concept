import { create } from "zustand";
import { v4 as uuidv4 } from "uuid";

export type NodeType = "section" | "list" | "static-text";

export interface BaseSchemaNode {
    id: string;
    parent_id: string | null;
};

// -- Section -- 
export interface SectionData {
    title: string;
    show_title: boolean;
    heading_level: number;
    page_before_break: boolean;
};

export interface SectionNode extends BaseSchemaNode {
    type: "section";
    data: SectionData;
};

// -- List -- 
export interface ListData {
    list_type: "bullet" | "numbered";
    spacing: "compact" | "normal" | "relaxed";
};

export interface ListNode extends BaseSchemaNode {
    type: "list";
    data: ListData;
};

// -- Static Text ---
export interface StaticTextData {
    text: string;
};

export interface StaticTextNode extends BaseSchemaNode {
    type: "static-text";
    data: StaticTextData;
}

export type SchemaNode = SectionNode | ListNode | StaticTextNode;

interface SchemaState {
    nodes: SchemaNode[];
    selectedNodeId: string | null;

    setNodes: (nodes: SchemaNode[]) => void;
    selectNode: (id: string | null) => void;
    addNode: (type: NodeType, parent_id: string | null) => void;
    removeNode: (id: string) => void;
    updateNodeData: (id: string, newData: Partial<SectionData & ListData & StaticTextData>) => void;
    reorderNodes: (newNodes: SchemaNode[]) => void;
};

export const useSchemaStore = create<SchemaState>((set) => ({
    nodes: [],
    selectedNodeId: null,

    setNodes: (nodes) => set({ nodes }),
    selectNode: (id) => set({ selectedNodeId: id }),
    addNode: (type, parent_id) => set((state) => {
        const newNodeId = uuidv4();
        let newNode: SchemaNode;

        if (type == "section") {
            newNode = {
                id: newNodeId,
                parent_id,
                type: "section",
                data: { title: "New Section", show_title: true, heading_level: 2, page_before_break: false }
            };
        } 
        else if (type == "static-text") {
            newNode = {
                id: newNodeId,
                parent_id,
                type: "static-text",
                data: { text: "Wprowadź statyczny tekst..." }
            }
        }
        else {
            newNode = {
                id: newNodeId,
                parent_id,
                type: "list",
                data: { list_type: "bullet", spacing: "normal" }
            };
        }

        return {
            nodes: [...state.nodes, newNode],
            selectedNodeId: newNodeId
        };
    }),

    removeNode: (id) => set((state) => {
        // A simple recursive function to remove a node and all its nested children
        const getDescendantIds = (parentId: string, allNodes: SchemaNode[]): string[] => {
            const children = allNodes.filter(n => n.parent_id === parentId);
            const childrenIds = children.map(c => c.id);
            const descendants = children.flatMap(c => getDescendantIds(c.id, allNodes));
            return [...childrenIds, ...descendants];
        };

        const idsToRemove = [id, ...getDescendantIds(id, state.nodes)];

        return {
            nodes: state.nodes.filter(n => !idsToRemove.includes(n.id)),
            selectedNodeId: state.selectedNodeId === id ? null : state.selectedNodeId
        };
    }),

    // Update the data object of a specific node from the right-side configuration panel
    updateNodeData: (id, newData) => set((state) => ({
        nodes: state.nodes.map(node =>
            node.id === id
                ? { ...node, data: { ...node.data, ...newData } } as SchemaNode
                : node
        )
    })),

    // Called when `@minoru/react-dnd-treeview` finishes a drag-and-drop operation
    reorderNodes: (newNodes) => set({ nodes: newNodes }),
}));