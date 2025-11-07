'use client';

import Link from 'next/link';

// Mock data for nearby veterinarians
const mockVeterinarians = [
  {
    id: '1',
    name: 'Paws & Claws Animal Hospital',
    address: '123 Main Street, San Francisco, CA 94102',
    phone: '(415) 555-0101',
    distance: '0.8 miles',
    rating: 4.8,
    reviews: 234,
    specialties: ['General Care', 'Emergency', 'Dental'],
    hours: 'Mon-Fri: 8AM-6PM, Sat: 9AM-4PM',
    imageUrl: '/api/placeholder/300/200',
  },
  {
    id: '2',
    name: 'Happy Tails Veterinary Clinic',
    address: '456 Oak Avenue, San Francisco, CA 94103',
    phone: '(415) 555-0102',
    distance: '1.2 miles',
    rating: 4.6,
    reviews: 189,
    specialties: ['General Care', 'Surgery'],
    hours: 'Mon-Fri: 9AM-7PM, Sun: 10AM-3PM',
    imageUrl: '/api/placeholder/300/200',
  },
  {
    id: '3',
    name: 'City Pet Care Center',
    address: '789 Market Boulevard, San Francisco, CA 94104',
    phone: '(415) 555-0103',
    distance: '1.5 miles',
    rating: 4.9,
    reviews: 312,
    specialties: ['General Care', 'Emergency', 'Dental', 'Surgery'],
    hours: 'Mon-Sun: 24/7 Emergency',
    imageUrl: '/api/placeholder/300/200',
  },
  {
    id: '4',
    name: 'Feline & Canine Specialists',
    address: '321 Pine Street, San Francisco, CA 94105',
    phone: '(415) 555-0104',
    distance: '2.1 miles',
    rating: 4.7,
    reviews: 156,
    specialties: ['General Care', 'Dental', 'Behavioral'],
    hours: 'Mon-Fri: 8AM-5PM',
    imageUrl: '/api/placeholder/300/200',
  },
];

// Mock data for vet-recommended pet products
const mockProducts = [
  {
    id: '1',
    name: 'Hill\'s Science Diet Adult Cat Food',
    category: 'Cat Food',
    description: 'Premium dry cat food recommended by veterinarians for optimal nutrition',
    price: 42.99,
    rating: 4.7,
    reviews: 1245,
    imageUrl: '/api/placeholder/200/200',
    vetRecommended: true,
    recommendedBy: 'Dr. Sarah Johnson, DVM',
  },
  {
    id: '2',
    name: 'Interactive Cat Puzzle Feeder',
    category: 'Toys & Enrichment',
    description: 'Mental stimulation toy that slows down eating and prevents boredom',
    price: 24.99,
    rating: 4.5,
    reviews: 892,
    imageUrl: '/api/placeholder/200/200',
    vetRecommended: true,
    recommendedBy: 'Paws & Claws Animal Hospital',
  },
  {
    id: '3',
    name: 'Feliway Classic Diffuser',
    category: 'Behavioral',
    description: 'Calming pheromone diffuser to reduce stress and anxiety in cats',
    price: 39.99,
    rating: 4.6,
    reviews: 2156,
    imageUrl: '/api/placeholder/200/200',
    vetRecommended: true,
    recommendedBy: 'Dr. Michael Chen, DVM',
  },
  {
    id: '4',
    name: 'Cat Dental Care Kit',
    category: 'Dental Health',
    description: 'Complete dental care kit with toothbrush, toothpaste, and dental treats',
    price: 18.99,
    rating: 4.4,
    reviews: 678,
    imageUrl: '/api/placeholder/200/200',
    vetRecommended: true,
    recommendedBy: 'Happy Tails Veterinary Clinic',
  },
  {
    id: '5',
    name: 'Premium Cat Scratching Post',
    category: 'Furniture',
    description: 'Tall, sturdy scratching post with multiple levels and hideaway',
    price: 79.99,
    rating: 4.8,
    reviews: 943,
    imageUrl: '/api/placeholder/200/200',
    vetRecommended: true,
    recommendedBy: 'City Pet Care Center',
  },
  {
    id: '6',
    name: 'Cat Weight Management Food',
    category: 'Cat Food',
    description: 'Veterinary-formulated weight control food for overweight cats',
    price: 38.99,
    rating: 4.6,
    reviews: 567,
    imageUrl: '/api/placeholder/200/200',
    vetRecommended: true,
    recommendedBy: 'Dr. Emily Rodriguez, DVM',
  },
];

export default function VetsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-lg shadow-xl p-8 mb-8">
          {/* Header */}
          <div className="mb-6">
            <Link
              href="/"
              className="inline-flex items-center text-indigo-600 hover:text-indigo-700 font-medium mb-4
                transition-colors duration-200"
            >
              <svg
                className="w-5 h-5 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10 19l-7-7m0 0l7-7m-7 7h18"
                />
              </svg>
              Back to Home
            </Link>
          </div>

          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                Vets & Products
              </h1>
              <p className="text-gray-600">
                Find nearby veterinarians and vet-recommended pet products
              </p>
            </div>
            <Link
              href="/profile"
              className="px-4 py-2 text-indigo-600 font-semibold rounded-lg
                hover:bg-indigo-50 transition-colors duration-200"
            >
              My Profile
            </Link>
          </div>
        </div>

        {/* Nearby Veterinarians Section */}
        <div className="bg-white rounded-lg shadow-xl p-8 mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-6">
            Nearby Veterinarians
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {mockVeterinarians.map((vet) => (
              <div
                key={vet.id}
                className="border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-gray-900 mb-2">
                      {vet.name}
                    </h3>
                    <div className="flex items-center mb-2">
                      <div className="flex items-center">
                        {[...Array(5)].map((_, i) => (
                          <svg
                            key={i}
                            className={`w-5 h-5 ${
                              i < Math.floor(vet.rating)
                                ? 'text-yellow-400'
                                : 'text-gray-300'
                            }`}
                            fill="currentColor"
                            viewBox="0 0 20 20"
                          >
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                          </svg>
                        ))}
                      </div>
                      <span className="ml-2 text-sm text-gray-600">
                        {vet.rating} ({vet.reviews} reviews)
                      </span>
                    </div>
                  </div>
                  <div className="ml-4 text-right">
                    <span className="inline-block px-3 py-1 bg-indigo-100 text-indigo-800 text-sm font-semibold rounded-full">
                      {vet.distance}
                    </span>
                  </div>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex items-center text-gray-600">
                    <svg
                      className="w-5 h-5 mr-2 text-gray-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                      />
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                      />
                    </svg>
                    <span className="text-sm">{vet.address}</span>
                  </div>
                  <div className="flex items-center text-gray-600">
                    <svg
                      className="w-5 h-5 mr-2 text-gray-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
                      />
                    </svg>
                    <span className="text-sm">{vet.phone}</span>
                  </div>
                  <div className="flex items-center text-gray-600">
                    <svg
                      className="w-5 h-5 mr-2 text-gray-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    <span className="text-sm">{vet.hours}</span>
                  </div>
                </div>

                <div className="flex flex-wrap gap-2">
                  {vet.specialties.map((specialty, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded"
                    >
                      {specialty}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Vet-Recommended Products Section */}
        <div className="bg-white rounded-lg shadow-xl p-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-6">
            Vet-Recommended Products
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {mockProducts.map((product) => (
              <div
                key={product.id}
                className="border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-shadow"
              >
                {/* Product Image Placeholder */}
                <div className="w-full h-48 bg-gradient-to-br from-gray-200 to-gray-300 flex items-center justify-center">
                  <svg
                    className="w-16 h-16 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                    />
                  </svg>
                </div>

                <div className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <span className="px-2 py-1 bg-indigo-100 text-indigo-800 text-xs font-semibold rounded">
                      {product.category}
                    </span>
                    <div className="flex items-center">
                      <svg
                        className="w-4 h-4 text-yellow-400"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                      <span className="ml-1 text-sm text-gray-600">{product.rating}</span>
                    </div>
                  </div>

                  <h3 className="text-lg font-bold text-gray-900 mb-2">
                    {product.name}
                  </h3>
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                    {product.description}
                  </p>

                  <div className="mb-3">
                    <div className="flex items-center text-xs text-indigo-600 mb-1">
                      <svg
                        className="w-4 h-4 mr-1"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                          clipRule="evenodd"
                        />
                      </svg>
                      Vet Recommended
                    </div>
                    <p className="text-xs text-gray-500">
                      by {product.recommendedBy}
                    </p>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-2xl font-bold text-gray-900">
                        ${product.price}
                      </span>
                      <span className="text-sm text-gray-500 ml-1">
                        ({product.reviews} reviews)
                      </span>
                    </div>
                    <button className="px-4 py-2 bg-indigo-600 text-white text-sm font-semibold rounded-lg
                      hover:bg-indigo-700 transition-colors duration-200">
                      View
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

