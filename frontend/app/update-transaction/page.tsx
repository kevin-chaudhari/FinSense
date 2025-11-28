"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { useForm, type SubmitHandler } from "react-hook-form"
import DatePicker from "react-datepicker"
import "react-datepicker/dist/react-datepicker.css"
import { toast, ToastContainer } from "react-toastify"
import "react-toastify/dist/ReactToastify.css"

type FormInputs = {
  amount: number
  type: "credit" | "debit"
  category: string
  description: string
  date: Date
}

const categories = [
  "Food & Dining",
  "Transportation",
  "Entertainment",
  "Shopping",
  "Utilities",
  "Healthcare",
  "Education",
  "Travel",
  "Other",
]

export default function UpdateTransaction() {
  const [isLoading, setIsLoading] = useState(false)
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
    watch,
  } = useForm<FormInputs>()

  const watchType = watch("type")

  const onSubmit: SubmitHandler<FormInputs> = async (data) => {
    setIsLoading(true)
    try {
      const response = await fetch("http://127.0.0.1:5000/update_user", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include", // 👈 Important: Send session cookie
        body: JSON.stringify({
          amount: data.amount,
          transaction_type: data.type,
          category: data.category,
          description: data.description,
          date: data.date,
        }),
      })

      const result = await response.json()

      if (response.ok) {
        toast.success(result.message || "Transaction updated successfully!")
        reset()
      } else {
        toast.error(result.error || "An error occurred. Please try again.")
      }
    } catch (error) {
      toast.error("Failed to connect to the server.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <motion.h1
        className="text-3xl font-bold mb-8 text-center text-indigo-800 dark:text-indigo-200"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        Update Transaction
      </motion.h1>
      <motion.form
        onSubmit={handleSubmit(onSubmit)}
        className="card p-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2, duration: 0.5 }}
      >
        <div className="mb-4">
          <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2" htmlFor="amount">
            Amount
          </label>
          <div className="relative">
            <span className="absolute left-3 top-0 text-gray-600">$</span>
            <input
              className={`input pl-7 ${errors.amount ? "border-red-500" : ""}`}
              id="amount"
              type="number"
              step="0.01"
              {...register("amount", {
                required: "Amount is required",
                min: { value: 0.01, message: "Amount must be positive" },
              })}
              placeholder="0.00"
              style={{ paddingTop: "0.1rem" }}
            />
          </div>
          {errors.amount && <p className="text-red-500 text-xs italic">{errors.amount.message}</p>}
        </div>

        <div className="mb-4">
          <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2">Type</label>
          <div className="flex space-x-4">
            <label className="inline-flex items-center">
              <input
                type="radio"
                className="form-radio text-indigo-600"
                value="credit"
                {...register("type", { required: "Transaction type is required" })}
              />
              <span className="ml-2">Credit</span>
            </label>
            <label className="inline-flex items-center">
              <input
                type="radio"
                className="form-radio text-indigo-600"
                value="debit"
                {...register("type", { required: "Transaction type is required" })}
              />
              <span className="ml-2">Debit</span>
            </label>
          </div>
          {errors.type && <p className="text-red-500 text-xs italic">{errors.type.message}</p>}
        </div>

        <div className="mb-4">
          <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2" htmlFor="category">
            Category
          </label>
          <select
            className={`input ${errors.category ? "border-red-500" : ""}`}
            id="category"
            {...register("category", { required: "Category is required" })}
          >
            <option value="">Select category</option>
            {categories.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
          {errors.category && <p className="text-red-500 text-xs italic">{errors.category.message}</p>}
        </div>

        <div className="mb-4">
          <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2" htmlFor="description">
            Description
          </label>
          <textarea
            className={`input ${errors.description ? "border-red-500" : ""}`}
            id="description"
            {...register("description", { required: "Description is required" })}
            placeholder="Type here..."
          ></textarea>
          {errors.description && <p className="text-red-500 text-xs italic">{errors.description.message}</p>}
        </div>

        <div className="mb-6">
          <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2" htmlFor="date">
            Date
          </label>
          <DatePicker
            selected={watch("date")}
            onChange={(date: Date) => setValue("date", date)}
            className={`input w-full ${errors.date ? "border-red-500" : ""}`}
            placeholderText="Select date"
          />
          {errors.date && <p className="text-red-500 text-xs italic">{errors.date.message}</p>}
        </div>

        <div className="flex items-center justify-between">
          <motion.button
            className={`btn ${watchType === "credit" ? "bg-green-600 hover:bg-green-700" : "bg-red-600 hover:bg-red-700"}`}
            type="submit"
            disabled={isLoading}
            whileTap={{ scale: 0.95 }}
          >
            {isLoading ? "Updating..." : `Submit ${watchType === "credit" ? "Credit" : "Debit"}`}
          </motion.button>
        </div>
      </motion.form>
      <ToastContainer position="bottom-right" autoClose={3000} />
    </div>
  )
}
