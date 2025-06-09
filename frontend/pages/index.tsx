// frontend/pages/index.tsx
import { useState } from 'react'
import { useQuery } from 'react-query'
import Head from 'next/head'
import Layout from '../components/Layout'
import ArticleCard from '../components/ArticleCard'
import SearchBar from '../components/SearchBar'
import FilterBar from '../components/FilterBar'
import LoadingSpinner from '../components/LoadingSpinner'
import { fetchArticles } from '../utils/api'

export default function Home() {
  const [filters, setFilters] = useState({})
  const [searchQuery, setSearchQuery] = useState('')

  const { data: articles, isLoading, error, refetch } = useQuery(
    ['articles', filters, searchQuery],
    () => fetchArticles({ ...filters, search: searchQuery }),
    {
      enabled: true,
      refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
    }
  )

  const handleFilterChange = (newFilters: any) => {
    setFilters(newFilters)
  }

  const handleSearch = (query: string) => {
    setSearchQuery(query)
  }

  if (error) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-red-600 mb-4">Error Loading Articles</h2>
            <p className="text-gray-600 mb-4">{(error as Error).message}</p>
            <button
              onClick={() => refetch()}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Try Again
            </button>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <Head>
        <title>AI News Aggregator - Intelligent News Curation</title>
        <meta name="description" content="AI-powered news aggregation with credibility scoring and smart summaries" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
            AI News Aggregator
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Intelligent news curation with AI-powered summaries and credibility analysis
          </p>
        </div>

        {/* Search and Filters */}
        <div className="mb-8">
          <SearchBar onSearch={handleSearch} />
          <FilterBar onFilterChange={handleFilterChange} />
        </div>

        {/* Articles Grid */}
        {isLoading ? (
          <LoadingSpinner />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {articles?.map((article: any) => (
              <ArticleCard key={article.id} article={article} />
            ))}
          </div>
        )}

        {articles && articles.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No articles found. Try adjusting your filters.</p>
          </div>
        )}
      </div>
    </Layout>
  )
}