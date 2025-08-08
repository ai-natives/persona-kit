import { PersonProfile } from '../types'

interface ProfileCardProps {
  profile: PersonProfile
}

export function ProfileCard({ profile }: ProfileCardProps) {
  const riskLevelText = ['Very Conservative', 'Conservative', 'Balanced', 'Aggressive', 'Very Aggressive']
  
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="mb-4">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-12 h-12 bg-nav-blue-100 rounded-full flex items-center justify-center">
            <span className="text-xl">👤</span>
          </div>
          <div>
            <h3 className="font-semibold text-lg">{profile.name}</h3>
            <p className="text-sm text-gray-600">{profile.current_role}</p>
          </div>
        </div>
        <div className="mt-2">
          <p className="text-sm text-gray-500">Target Role</p>
          <p className="font-medium">{profile.target_role}</p>
        </div>
      </div>

      <div className="space-y-3 pt-4 border-t">
        <div>
          <p className="text-sm text-gray-500 mb-1">Risk Level</p>
          <div className="flex items-center gap-2">
            <div className="flex gap-1">
              {[1, 2, 3, 4, 5].map((level) => (
                <div
                  key={level}
                  className={`w-2 h-6 rounded ${
                    level <= profile.risk_level
                      ? level <= 2 ? 'bg-green-500' : level <= 3 ? 'bg-yellow-500' : 'bg-red-500'
                      : 'bg-gray-300'
                  }`}
                />
              ))}
            </div>
            <span className="text-sm">{riskLevelText[profile.risk_level - 1]}</span>
          </div>
        </div>

        <div>
          <p className="text-sm text-gray-500">Learning Style</p>
          <p className="font-medium capitalize">{profile.learning_style.replace('_', ' ')}</p>
        </div>

        <div>
          <p className="text-sm text-gray-500">Networking</p>
          <p className="font-medium capitalize">{profile.networking_comfort}</p>
        </div>
      </div>
    </div>
  )
}