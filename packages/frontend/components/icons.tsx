import {
  LucideProps,
  Moon,
  SunMedium,
  type Icon as LucideIcon,
  Spinner,
  HeartPulse,
  Users,
  Wifi,
  ShieldAlert,
  Timer,
  Database,
  CheckCircle,
  AlertTriangle,
  XCircle,
  HelpCircle,
  Download,
} from 'lucide-react';

export type Icon = LucideIcon;

export const Icons = {
  sun: SunMedium,
  moon: Moon,
  spinner: (props: LucideProps) => <Spinner {...props} />,
  heartPulse: (props: LucideProps) => <HeartPulse {...props} />,
  users: (props: LucideProps) => <Users {...props} />,
  wifi: (props: LucideProps) => <Wifi {...props} />,
  shieldAlert: (props: LucideProps) => <ShieldAlert {...props} />,
  timer: (props: LucideProps) => <Timer {...props} />,
  database: (props: LucideProps) => <Database {...props} />,
  checkCircle: (props: LucideProps) => <CheckCircle {...props} />,
  alertTriangle: (props: LucideProps) => <AlertTriangle {...props} />,
  xCircle: (props: LucideProps) => <XCircle {...props} />,
  helpCircle: (props: LucideProps) => <HelpCircle {...props} />,
  download: (props: LucideProps) => <Download {...props} />,
};