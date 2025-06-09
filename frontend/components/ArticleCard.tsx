import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  BookmarkIcon, 
  ShareIcon, 
  ClockIcon,
  ExclamationTriangleIcon,
  CheckBadgeIcon 
} from '@heroicons/react/24/outline'
import { BookmarkIcon as BookmarkSolidIcon } from '@heroicons/react/24/solid'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

interface ArticleCardProps {
  article: {
    id: string
    title: string
    summary: string
    source: string
    category: string
    published_date: string
    reading_time: number
    fake_news_score: number
    fake_news_confidence: number
    url: string
    image_url?: string
  }
}

export default function ArticleCard({ article }: ArticleCardProps) {
  const [isBookmarked, setIsBookmarked] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)

  const credibilityColor = 
    article.fake_news_score >= 0.8 ? 'text-green-600' :
    article.fake_news_score >= 0.6 ? 'text-yellow-600' : 'text-red-600'

  const credibilityIcon = 
    article.fake_news_score >= 0.8 ? CheckBadgeIcon : ExclamationTriangleIcon

  const handleBookmark = async () => {
    try {
      // API call to bookmark/unbookmark
      setIsBookmarked(!isBookmarked)
      toast.success(isBookmarked ? 'Removed from bookmarks' : 'Added to bookmarks')
    } catch (error) {
      toast.error('Failed to update bookmark')
    }
  }

  const handleShare = async () => {
    try {
      await navigator.share({
        title: article.title,
        text: article.summary,
        url: article.url
      })
    } catch (error) {
      // Fallback to clipboard
      await navigator.clipboard.writeText(article.url)
      toast.success('Link copied to clipboard')
    }
  }

  const CredibilityIcon = credibilityIcon

  return (
    <motion.div
      whileHover={{ y: -5, scale: 1.02 }}
      className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-all duration-300"
    >
      {/* Image */}
      {article.image_url && (
        <div className="relative h-48 overflow-hidden">
          <img
            src={article.image_url}
            alt={article.title}
            className="w-full h-full object-cover"
          />
          <div className="absolute top-3 left-3">
            <span className="bg-blue-600 text-white px-2 py-1 rounded-full text-xs font-medium">
              {article.category}
            </span>
          </div>
        </div>
      )}

      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <span className="font-medium">{article.source}</span>
            <span>•</span>
            <span>{format(new Date(article.published_date), 'MMM d, yyyy')}</span>
          </div>
          <div className="flex items-center space-x-1">
            <CredibilityIcon className={`h-5 w-5 ${credibilityColor}`} />
            <span className={`text-sm font-medium ${credibilityColor}`}>
              {Math.round(article.fake_news_score * 100)}%
            </span>
          </div>
        </div>

        {/* Title */}
        <h3 className="text-lg font-bold text-gray-900 mb-3 line-clamp-2 leading-tight">
          {article.title}
        </h3>

        {/* Summary */}
        <p className={`text-gray-600 mb-4 leading-relaxed ${
          isExpanded ? '' : 'line-clamp-3'
        }`}>
          {article.summary}
        </p>

        {/* Expand/Collapse */}
        {article.summary.length > 150 && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-blue-600 text-sm font-medium hover:text-blue-700 mb-4"
          >
            {isExpanded ? 'Show less' : 'Read more'}
          </button>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-100">
          <div className="flex items-center space-x-4 text-sm text-gray-500">
            <div className="flex items-center space-x-1">
              <ClockIcon className="h-4 w-4" />
              <span>{article.reading_time} min read</span>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handleBookmark}
              className="p-2 rounded-full hover:bg-gray-100 transition-colors"
            >
              {isBookmarked ? (
                <BookmarkSolidIcon className="h-5 w-5 text-blue-600" />
              ) : (
                <BookmarkIcon className="h-5 w-5 text-gray-600" />
              )}
            </button>
            <button
              onClick={handleShare}
              className="p-2 rounded-full hover:bg-gray-100 transition-colors"
            >
              <ShareIcon className="h-5 w-5 text-gray-600" />
            </button>
            <a
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
            >
              Read Full Article
            </a>
          </div>
        </div>
      </div>
    </motion.div>
  )
}