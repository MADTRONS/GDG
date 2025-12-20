import { 
  HeartPulse, 
  Briefcase, 
  GraduationCap, 
  DollarSign, 
  Users, 
  Star,
  HelpCircle,
  LucideIcon
} from 'lucide-react';

const iconMap: Record<string, LucideIcon> = {
  'heart-pulse': HeartPulse,
  'briefcase': Briefcase,
  'graduation-cap': GraduationCap,
  'dollar-sign': DollarSign,
  'users': Users,
  'star': Star,
};

export function getIcon(iconName: string): LucideIcon {
  return iconMap[iconName] || HelpCircle;
}
