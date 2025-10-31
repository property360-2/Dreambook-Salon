import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { api } from '../../lib/api.js';
import { useAuth } from '../../hooks/useAuth.js';

const defaultValues = {
  name: '',
  description: '',
  stock: 0,
  unit: '',
  threshold: 0,
  isActive: true,
};

export function InventoryManager() {
  const { token, user } = useAuth();
  const isAdmin = user?.role === 'ADMIN';
  const queryClient = useQueryClient();
  const [formError, setFormError] = useState(null);
  const [editingItem, setEditingItem] = useState(null);

  const {
    data,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ['inventory'],
    queryFn: () => api.inventory.list(token),
    enabled: Boolean(token && isAdmin),
  });

  const { register, handleSubmit, reset } = useForm({
    defaultValues,
  });

  const mutation = useMutation({
    mutationFn: (values) => {
      const payload = {
        name: values.name.trim(),
        description: values.description?.trim() || undefined,
        stock: Number(values.stock ?? 0),
        unit: values.unit?.trim() || undefined,
        threshold: Number(values.threshold ?? 0),
        isActive: Boolean(values.isActive),
      };

      return editingItem
        ? api.inventory.update(token, editingItem.id, payload)
        : api.inventory.create(token, payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      setFormError(null);
      setEditingItem(null);
      reset(defaultValues);
    },
    onError: (err) => {
      setFormError(err.message ?? 'Unable to save inventory item');
    },
  });

  const onSubmit = (values) => mutation.mutate(values);

  const handleEdit = (item) => {
    setEditingItem(item);
    reset({
      name: item.name,
      description: item.description ?? '',
      stock: item.stock ?? 0,
      unit: item.unit ?? '',
      threshold: item.threshold ?? 0,
      isActive: item.isActive,
    });
  };

  const handleCancelEdit = () => {
    setEditingItem(null);
    reset(defaultValues);
    setFormError(null);
  };

  if (!isAdmin) {
    return null;
  }

  return (
    <section className="card">
      <header style={{ marginBottom: '1rem' }}>
        <h2 style={{ margin: 0 }}>
          Inventory management {editingItem ? '(editing)' : ''}
        </h2>
        <p className="muted" style={{ margin: 0 }}>
          Track consumables, update stock, and configure low-stock thresholds.
        </p>
      </header>

      <form className="form" onSubmit={handleSubmit(onSubmit)} noValidate>
        <div className="field">
          <label htmlFor="inventory-name">Name</label>
          <input
            id="inventory-name"
            type="text"
            {...register('name', { required: 'Name is required' })}
          />
        </div>

        <div className="field">
          <label htmlFor="inventory-description">Description</label>
          <textarea
            id="inventory-description"
            rows={2}
            {...register('description')}
          />
        </div>

        <div
          style={{
            display: 'grid',
            gap: '0.75rem',
            gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
          }}
        >
          <div className="field">
            <label htmlFor="inventory-stock">Stock</label>
            <input
              id="inventory-stock"
              type="number"
              min={0}
              step={1}
              {...register('stock', { valueAsNumber: true })}
            />
          </div>
          <div className="field">
            <label htmlFor="inventory-unit">Unit</label>
            <input
              id="inventory-unit"
              type="text"
              {...register('unit')}
            />
          </div>
          <div className="field">
            <label htmlFor="inventory-threshold">Low stock threshold</label>
            <input
              id="inventory-threshold"
              type="number"
              min={0}
              step={1}
              {...register('threshold', { valueAsNumber: true })}
            />
          </div>
        </div>

        <div className="field" style={{ flexDirection: 'row', gap: '0.5rem' }}>
          <input
            id="inventory-active"
            type="checkbox"
            {...register('isActive')}
          />
          <label htmlFor="inventory-active">Active item</label>
        </div>

        {formError && <p className="error">{formError}</p>}

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            className="button"
            type="submit"
            disabled={mutation.isPending}
          >
            {editingItem ? 'Update inventory' : 'Add inventory item'}
          </button>
          {editingItem && (
            <button
              type="button"
              className="button secondary"
              onClick={handleCancelEdit}
            >
              Cancel edit
            </button>
          )}
        </div>
      </form>

      <div style={{ marginTop: '2rem' }}>
        <h3 style={{ marginBottom: '0.75rem' }}>Current stock</h3>
        {isLoading && <p className="muted">Loading inventory...</p>}
        {isError && (
          <p className="error">
            Failed to load inventory: {error.message ?? 'Unknown error'}
          </p>
        )}
        {!isLoading && !isError && data?.inventory?.length === 0 && (
          <p className="muted">No inventory items yet.</p>
        )}
        {!isLoading && !isError && data?.inventory?.length > 0 && (
          <div className="table-responsive">
            <table className="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Stock</th>
                  <th>Unit</th>
                  <th>Threshold</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {data.inventory.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <strong>{item.name}</strong>
                      {item.description && (
                        <p className="muted" style={{ margin: 0 }}>
                          {item.description}
                        </p>
                      )}
                    </td>
                    <td>{item.stock}</td>
                    <td>{item.unit ?? '-'}</td>
                    <td>{item.threshold}</td>
                    <td>{item.isActive ? 'Active' : 'Inactive'}</td>
                    <td>
                      <button
                        type="button"
                        className="button secondary"
                        onClick={() => handleEdit(item)}
                      >
                        Edit
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}
