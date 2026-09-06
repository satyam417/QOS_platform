"use client";

import { useState } from "react";

type Service = {
  id: number;
  name: string;
  category: string;
  description: string;
  price: number;
  duration: number;
  pincodes: string[];
  status: "Active" | "Disabled";
};

type ServiceForm = {
  name: string;
  category: string;
  description: string;
  price: string;
  duration: string;
  pincodes: string;
};

const categories = [
  "Cleaning",
  "Appliance Repair",
  "Plumbing",
  "Electrical",
  "Painting",
];

const initialServices: Service[] = [
  {
    id: 1,
    name: "Deep Home Cleaning",
    category: "Cleaning",
    description: "Complete deep cleaning service for homes.",
    price: 1499,
    duration: 120,
    pincodes: ["560001", "560002"],
    status: "Active",
  },
  {
    id: 2,
    name: "AC Service",
    category: "Appliance Repair",
    description: "Professional AC servicing and maintenance.",
    price: 799,
    duration: 60,
    pincodes: ["560003", "560004"],
    status: "Disabled",
  },
];

const emptyForm: ServiceForm = {
  name: "",
  category: "",
  description: "",
  price: "",
  duration: "",
  pincodes: "",
};

export default function Home() {
  const [services, setServices] = useState<Service[]>(initialServices);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState<ServiceForm>(emptyForm);
  const [error, setError] = useState("");

  const openCreateForm = () => {
    setEditingId(null);
    setForm(emptyForm);
    setError("");
    setShowForm(true);
  };

  const openEditForm = (service: Service) => {
    setEditingId(service.id);
    setForm({
      name: service.name,
      category: service.category,
      description: service.description,
      price: String(service.price),
      duration: String(service.duration),
      pincodes: service.pincodes.join(", "),
    });
    setError("");
    setShowForm(true);
  };

  const closeForm = () => {
    setShowForm(false);
    setEditingId(null);
    setForm(emptyForm);
    setError("");
  };

  const handleChange = (
    field: keyof ServiceForm,
    value: string
  ) => {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!form.name.trim()) {
      setError("Service name is required.");
      return;
    }

    if (!form.category) {
      setError("Please select a category.");
      return;
    }

    if (!form.price || Number(form.price) <= 0) {
      setError("Price must be greater than 0.");
      return;
    }

    if (!form.duration || Number(form.duration) <= 0) {
      setError("Duration must be greater than 0.");
      return;
    }

    const pincodes = form.pincodes
      .split(",")
      .map((pincode) => pincode.trim())
      .filter(Boolean);

    if (pincodes.length === 0) {
      setError("At least one pincode is required.");
      return;
    }

    if (editingId !== null) {
      setServices((current) =>
        current.map((service) =>
          service.id === editingId
            ? {
                ...service,
                name: form.name.trim(),
                category: form.category,
                description: form.description.trim(),
                price: Number(form.price),
                duration: Number(form.duration),
                pincodes,
              }
            : service
        )
      );
    } else {
      const newService: Service = {
        id: Date.now(),
        name: form.name.trim(),
        category: form.category,
        description: form.description.trim(),
        price: Number(form.price),
        duration: Number(form.duration),
        pincodes,
        status: "Active",
      };

      setServices((current) => [...current, newService]);
    }

    closeForm();
  };

  const toggleStatus = (id: number) => {
    setServices((current) =>
      current.map((service) =>
        service.id === id
          ? {
              ...service,
              status:
                service.status === "Active"
                  ? "Disabled"
                  : "Active",
            }
          : service
      )
    );
  };

  return (
    <main className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="border-b bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">
              Vendor Portal
            </h1>
            <p className="mt-1 text-sm text-slate-500">
              Manage your services and listings
            </p>
          </div>

          <button
            onClick={openCreateForm}
            className="rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-700"
          >
            + Add Service
          </button>
        </div>
      </header>

      {/* Services */}
      <section className="mx-auto max-w-7xl px-6 py-8">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-slate-900">
              My Services
            </h2>
            <p className="mt-1 text-sm text-slate-500">
              View and manage the services you offer.
            </p>
          </div>

          <div className="rounded-lg bg-white px-4 py-2 text-sm text-slate-600 shadow-sm">
            Total Services:{" "}
            <span className="font-semibold text-slate-900">
              {services.length}
            </span>
          </div>
        </div>

        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {services.map((service) => (
            <div
              key={service.id}
              className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
            >
              <div className="mb-4 flex items-start justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-slate-900">
                    {service.name}
                  </h3>

                  <p className="mt-1 text-sm text-slate-500">
                    {service.category}
                  </p>
                </div>

                <span
                  className={`rounded-full px-3 py-1 text-xs font-semibold ${
                    service.status === "Active"
                      ? "bg-green-100 text-green-700"
                      : "bg-slate-100 text-slate-600"
                  }`}
                >
                  {service.status}
                </span>
              </div>

              <p className="mb-4 text-sm text-slate-500">
                {service.description}
              </p>

              <div className="space-y-2 border-t border-slate-100 pt-4 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-500">Price</span>
                  <span className="font-semibold text-slate-900">
                    ₹{service.price}
                  </span>
                </div>

                <div className="flex justify-between">
                  <span className="text-slate-500">Duration</span>
                  <span className="text-slate-900">
                    {service.duration} mins
                  </span>
                </div>

                <div>
                  <p className="text-slate-500">
                    Service Pincodes
                  </p>

                  <div className="mt-2 flex flex-wrap gap-2">
                    {service.pincodes.map((pincode) => (
                      <span
                        key={pincode}
                        className="rounded-md bg-slate-100 px-2 py-1 text-xs text-slate-700"
                      >
                        {pincode}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="mt-5 flex gap-2 border-t border-slate-100 pt-4">
                <button
                  onClick={() => openEditForm(service)}
                  className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
                >
                  Edit
                </button>

                <button
                  onClick={() => toggleStatus(service.id)}
                  className={`flex-1 rounded-lg px-3 py-2 text-sm font-medium ${
                    service.status === "Active"
                      ? "bg-red-50 text-red-600 hover:bg-red-100"
                      : "bg-green-50 text-green-700 hover:bg-green-100"
                  }`}
                >
                  {service.status === "Active"
                    ? "Disable"
                    : "Enable"}
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Create / Edit Modal */}
      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
          <div className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-2xl bg-white p-6 shadow-xl">
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-slate-900">
                  {editingId !== null
                    ? "Edit Service"
                    : "Create Service"}
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Enter your service listing details.
                </p>
              </div>

              <button
                onClick={closeForm}
                className="text-2xl text-slate-400 hover:text-slate-700"
              >
                ×
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Service Name
                </label>

                <input
                  value={form.name}
                  onChange={(event) =>
                    handleChange("name", event.target.value)
                  }
                  placeholder="e.g. Deep Home Cleaning"
                  className="w-full rounded-lg border border-slate-300 px-4 py-2.5 outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Category
                </label>

                <select
                  value={form.category}
                  onChange={(event) =>
                    handleChange("category", event.target.value)
                  }
                  className="w-full rounded-lg border border-slate-300 px-4 py-2.5 outline-none focus:border-blue-500"
                >
                  <option value="">Select category</option>

                  {categories.map((category) => (
                    <option key={category} value={category}>
                      {category}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Description
                </label>

                <textarea
                  value={form.description}
                  onChange={(event) =>
                    handleChange(
                      "description",
                      event.target.value
                    )
                  }
                  placeholder="Describe your service"
                  rows={4}
                  className="w-full rounded-lg border border-slate-300 px-4 py-2.5 outline-none focus:border-blue-500"
                />
              </div>

              <div className="grid gap-5 sm:grid-cols-2">
                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-700">
                    Price (₹)
                  </label>

                  <input
                    type="number"
                    min="1"
                    value={form.price}
                    onChange={(event) =>
                      handleChange("price", event.target.value)
                    }
                    placeholder="1499"
                    className="w-full rounded-lg border border-slate-300 px-4 py-2.5 outline-none focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-700">
                    Duration (minutes)
                  </label>

                  <input
                    type="number"
                    min="1"
                    value={form.duration}
                    onChange={(event) =>
                      handleChange(
                        "duration",
                        event.target.value
                      )
                    }
                    placeholder="120"
                    className="w-full rounded-lg border border-slate-300 px-4 py-2.5 outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Service Pincodes
                </label>

                <input
                  value={form.pincodes}
                  onChange={(event) =>
                    handleChange("pincodes", event.target.value)
                  }
                  placeholder="560001, 560002, 560003"
                  className="w-full rounded-lg border border-slate-300 px-4 py-2.5 outline-none focus:border-blue-500"
                />

                <p className="mt-1 text-xs text-slate-500">
                  Enter multiple pincodes separated by commas.
                </p>
              </div>

              {error && (
                <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-600">
                  {error}
                </div>
              )}

              <div className="flex justify-end gap-3 border-t pt-5">
                <button
                  type="button"
                  onClick={closeForm}
                  className="rounded-lg border border-slate-300 px-5 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-700"
                >
                  {editingId !== null
                    ? "Save Changes"
                    : "Create Service"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </main>
  );
}