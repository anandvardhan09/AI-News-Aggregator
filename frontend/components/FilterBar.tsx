import { useState, useEffect } from 'react'
import { useQuery } from 'react-query'
import { FunnelIcon } from '@heroicons/react/24/outline'
import { fetchCategories, fetchSources } from '../utils/api'

interface FilterBarProps {
  onFilterChange: (filters: any) => void
}

export default function FilterBar({ onFilterChange }: FilterBarProps) {
  const [filters, setFilters] = useState({
    category: '',
    source: '',
    minCredibility: 0.5
  })

  const { data: categories } = useQuery('categories', fetchCategories)
  const { data: sources } = useQuery('sources', fetchSources)

  const handleFilterChange = (key: string, value: any) => {
    const newFilters = { ...filters, [key]: value }
    setFilters(newFilters)
    onFilterChange(newFilters)
  }

  return (
    <div className="flex flex-wrap gap-4 items-center">
      <div className="flex items-center space-x-2">
        <FunnelIcon className="h-5 w-5 text-gray-500" />
        <span className="text-sm font-medium text-gray-700">Filters:</span>
      </div>

      {/* Category Filter */}
      <select
        value={filters.category}
        onChange={(e) => handleFilterChange('category', e.target.value)}
        className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        <option value="">All Categories</option>
        {categories?.categories.map((category: string) => (
          <option key={category} value={category}>
            {category.charAt(0).toUpperCase() + category.slice(1)}
          </option>
        ))}
      </select>

      {/* Source Filter */}
      <select
        value={filters.source}
        onChange={(e) => handleFilterChange('source', e.target.value)}
        className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        <option value="">All Sources</option>
        {sources?.sources.slice(0, 10).map((source: string) => (
          <option key={source} value={source}>
            {source}
          </option>
        ))}
      </select>

      {/* Credibility Filter */}
      <div className="flex items-center space-x-2">
        <label className="text-sm text-gray-700">Min Credibility:</label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={filters.minCredibility}
          onChange={(e) => handleFilterChange('minCredibility', parseFloat(e.target.value))}
          className="w-20"
        />
        <span className="text-sm text-gray-600">
          {Math.round(filters.minCredibility * 100)}%
        </span>
      </div>

      {/* Clear Filters */}
      <button
        onClick={() => {
          const resetFilters = { category: '', source: '', minCredibility: 0.5 }
          setFilters(resetFilters)
          onFilterChange(resetFilters)
        }}
        className="text-sm text-blue-600 hover:text-blue-700 font-medium"
      >
        Clear All
      </button>
    </div>
  )
}