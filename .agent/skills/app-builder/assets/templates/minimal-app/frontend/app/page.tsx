"use client";

import { useState, useEffect } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Item {
  id: number;
  name: string;
  description: string;
  completed: boolean;
}

export default function Home() {
  const [items, setItems] = useState<Item[]>([]);
  const [newItem, setNewItem] = useState({ name: "", description: "" });
  const [loading, setLoading] = useState(false);

  // Fetch items
  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    const res = await fetch(`${API_URL}/items`);
    const data = await res.json();
    setItems(data);
  };

  const createItem = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    await fetch(`${API_URL}/items`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...newItem, completed: false }),
    });
    
    setNewItem({ name: "", description: "" });
    await fetchItems();
    setLoading(false);
  };

  const toggleComplete = async (item: Item) => {
    await fetch(`${API_URL}/items/${item.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...item, completed: !item.completed }),
    });
    await fetchItems();
  };

  const deleteItem = async (id: number) => {
    await fetch(`${API_URL}/items/${id}`, { method: "DELETE" });
    await fetchItems();
  };

  return (
    <main style={{ maxWidth: 600, margin: "0 auto", padding: 20 }}>
      <h1>Minimal App</h1>
      <p>Simple CRUD example with Next.js + FastAPI</p>

      {/* Create Form */}
      <form onSubmit={createItem} style={{ marginBottom: 20 }}>
        <input
          type="text"
          placeholder="Item name"
          value={newItem.name}
          onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
          required
          style={{ marginRight: 8, padding: 8 }}
        />
        <input
          type="text"
          placeholder="Description"
          value={newItem.description}
          onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
          style={{ marginRight: 8, padding: 8 }}
        />
        <button type="submit" disabled={loading} style={{ padding: 8 }}>
          {loading ? "Adding..." : "Add"}
        </button>
      </form>

      {/* Items List */}
      <ul style={{ listStyle: "none", padding: 0 }}>
        {items.map((item) => (
          <li
            key={item.id}
            style={{
              padding: 12,
              marginBottom: 8,
              border: "1px solid #ddd",
              borderRadius: 4,
              display: "flex",
              alignItems: "center",
              gap: 12,
            }}
          >
            <input
              type="checkbox"
              checked={item.completed}
              onChange={() => toggleComplete(item)}
            />
            <span
              style={{
                flex: 1,
                textDecoration: item.completed ? "line-through" : "none",
              }}
            >
              <strong>{item.name}</strong>
              {item.description && (
                <span style={{ color: "#666", marginLeft: 8 }}>
                  - {item.description}
                </span>
              )}
            </span>
            <button
              onClick={() => deleteItem(item.id)}
              style={{
                padding: "4px 8px",
                background: "#ff4444",
                color: "white",
                border: "none",
                borderRadius: 4,
                cursor: "pointer",
              }}
            >
              Delete
            </button>
          </li>
        ))}
      </ul>

      {items.length === 0 && (
        <p style={{ color: "#666", textAlign: "center" }}>
          No items yet. Create one above!
        </p>
      )}
    </main>
  );
}
