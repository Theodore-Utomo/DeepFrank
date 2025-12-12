'use client';

import Link from 'next/link';
import { DashboardLayout } from '@/components/layouts/DashboardLayout';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { MapPin, Phone, Clock, Star, CheckCircle2, ShoppingBag } from 'lucide-react';

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
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="space-y-2">
          <h1 className="text-4xl font-bold text-foreground">Vets & Products</h1>
          <p className="text-muted-foreground">
            Find nearby veterinarians and vet-recommended pet products
          </p>
        </div>

        {/* Nearby Veterinarians Section */}
        <Card className="p-6">
          <h2 className="text-2xl font-bold text-foreground mb-6">
            Nearby Veterinarians
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {mockVeterinarians.map((vet) => (
              <Card
                key={vet.id}
                className="p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-foreground mb-2">
                      {vet.name}
                    </h3>
                    <div className="flex items-center gap-2 mb-2">
                      <div className="flex items-center">
                        {[...Array(5)].map((_, i) => (
                          <Star
                            key={i}
                            className={`h-4 w-4 ${
                              i < Math.floor(vet.rating)
                                ? 'fill-yellow-400 text-yellow-400'
                                : 'text-muted-foreground'
                            }`}
                          />
                        ))}
                      </div>
                      <span className="text-sm text-muted-foreground">
                        {vet.rating} ({vet.reviews} reviews)
                      </span>
                    </div>
                  </div>
                  <Badge variant="secondary">{vet.distance}</Badge>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex items-center text-sm text-muted-foreground">
                    <MapPin className="w-4 h-4 mr-2" />
                    <span>{vet.address}</span>
                  </div>
                  <div className="flex items-center text-sm text-muted-foreground">
                    <Phone className="w-4 h-4 mr-2" />
                    <span>{vet.phone}</span>
                  </div>
                  <div className="flex items-center text-sm text-muted-foreground">
                    <Clock className="w-4 h-4 mr-2" />
                    <span>{vet.hours}</span>
                  </div>
                </div>

                <div className="flex flex-wrap gap-2">
                  {vet.specialties.map((specialty, idx) => (
                    <Badge key={idx} variant="outline" className="text-xs">
                      {specialty}
                    </Badge>
                  ))}
                </div>
              </Card>
            ))}
          </div>
        </Card>

        {/* Vet-Recommended Products Section */}
        <Card className="p-6">
          <h2 className="text-2xl font-bold text-foreground mb-6">
            Vet-Recommended Products
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {mockProducts.map((product) => (
              <Card
                key={product.id}
                className="overflow-hidden hover:shadow-lg transition-shadow"
              >
                {/* Product Image Placeholder */}
                <div className="w-full h-48 bg-gradient-to-br from-muted to-muted/50 flex items-center justify-center">
                  <ShoppingBag className="w-16 h-16 text-muted-foreground" />
                </div>

                <div className="p-4 space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <Badge variant="secondary" className="text-xs">
                      {product.category}
                    </Badge>
                    <div className="flex items-center gap-1">
                      <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                      <span className="text-sm text-muted-foreground">{product.rating}</span>
                    </div>
                  </div>

                  <h3 className="text-lg font-bold text-foreground">
                    {product.name}
                  </h3>
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {product.description}
                  </p>

                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-xs text-primary">
                      <CheckCircle2 className="h-4 w-4" />
                      <span className="font-medium">Vet Recommended</span>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      by {product.recommendedBy}
                    </p>
                  </div>

                  <div className="flex items-center justify-between pt-2 border-t border-border">
                    <div>
                      <span className="text-2xl font-bold text-foreground">
                        ${product.price}
                      </span>
                      <span className="text-sm text-muted-foreground ml-1">
                        ({product.reviews} reviews)
                      </span>
                    </div>
                    <Button variant="outline" size="sm">
                      View
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </Card>
      </div>
    </DashboardLayout>
  );
}
