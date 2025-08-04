import { useState } from 'react';
import { 
  CreditCard,
  Users,
  Calendar,
  ArrowUpRight
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export default function Monetization() {
  const [revenue] = useState({
    total: 42500,
    monthly: 4250,
    growth: 12.5,
    sources: [
      { name: 'Freelance Projects', amount: 25000, percentage: 59 },
      { name: 'Code Reviews', amount: 8500, percentage: 20 },
      { name: 'Consulting', amount: 6000, percentage: 14 },
      { name: 'Other', amount: 3000, percentage: 7 },
    ]
  });

  const [opportunities] = useState([
    { id: 1, title: 'E-commerce Platform', client: 'TechCorp', budget: '$5,000 - $8,000', deadline: '2 weeks', status: 'new' },
    { id: 2, title: 'Mobile App Backend', client: 'StartupXYZ', budget: '$3,000 - $5,000', deadline: '3 weeks', status: 'pending' },
    { id: 3, title: 'API Integration', client: 'BigCo', budget: '$2,000 - $3,000', deadline: '1 week', status: 'accepted' },
  ]);

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Monetization</h1>
        <p className="text-gray-600 mt-1">Track your revenue and discover new opportunities</p>
      </div>

      {/* Revenue Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Total Revenue</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${revenue.total.toLocaleString()}</div>
            <div className="flex items-center gap-1 mt-1">
              <ArrowUpRight className="w-4 h-4 text-green-500" />
              <span className="text-sm text-green-600">+{revenue.growth}%</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Monthly Average</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${revenue.monthly.toLocaleString()}</div>
            <p className="text-sm text-gray-500 mt-1">Per month</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Active Projects</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">7</div>
            <p className="text-sm text-gray-500 mt-1">In progress</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Opportunities</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{opportunities.length}</div>
            <p className="text-sm text-gray-500 mt-1">Available</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-12 gap-6">
        {/* Revenue Sources */}
        <div className="col-span-5">
          <Card>
            <CardHeader>
              <CardTitle>Revenue Sources</CardTitle>
              <CardDescription>Breakdown of income by category</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {revenue.sources.map((source) => (
                <div key={source.name} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">{source.name}</span>
                    <span className="text-sm text-gray-600">${source.amount.toLocaleString()}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="gradient-primary h-2 rounded-full transition-all duration-500"
                      style={{ width: `${source.percentage}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-500">{source.percentage}% of total</p>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Opportunities */}
        <div className="col-span-7">
          <Card>
            <CardHeader>
              <CardTitle>New Opportunities</CardTitle>
              <CardDescription>Latest freelance projects matching your skills</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {opportunities.map((opp) => (
                  <div key={opp.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-900">{opp.title}</h4>
                        <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                          <span className="flex items-center gap-1">
                            <Users className="w-4 h-4" />
                            {opp.client}
                          </span>
                          <span className="flex items-center gap-1">
                            <CreditCard className="w-4 h-4" />
                            {opp.budget}
                          </span>
                          <span className="flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            {opp.deadline}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {opp.status === 'new' && (
                          <span className="badge-info">New</span>
                        )}
                        {opp.status === 'pending' && (
                          <span className="badge-warning">Pending</span>
                        )}
                        {opp.status === 'accepted' && (
                          <span className="badge-success">Accepted</span>
                        )}
                        <Button size="sm" className="gradient-primary text-white">
                          View Details
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}