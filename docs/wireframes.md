# College Student Counseling Platform - Wireframe Specifications

**Version:** 1.0  
**Date:** December 19, 2025  
**Purpose:** Detailed wireframe specifications for UI/UX design implementation

---

## Design System Foundation

### Color Palette
- **Primary Blue:** #4A90E2 (trust, calm)
- **Secondary Green:** #6FCF97 (health, growth)
- **Neutral Gray 100:** #F5F5F5 (backgrounds)
- **Neutral Gray 900:** #333333 (text)
- **White:** #FFFFFF
- **Error Red:** #E74C3C
- **Success Green:** #27AE60
- **Warning Yellow:** #F39C12

### Typography
- **Font Family:** Inter (fallback: system-ui, sans-serif)
- **Heading 1:** 32px, font-weight 700, line-height 1.2
- **Heading 2:** 24px, font-weight 600, line-height 1.3
- **Heading 3:** 20px, font-weight 600, line-height 1.4
- **Body:** 16px, font-weight 400, line-height 1.6
- **Small:** 14px, font-weight 400, line-height 1.5
- **Caption:** 12px, font-weight 400, line-height 1.4

### Spacing Scale
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px
- 2xl: 48px
- 3xl: 64px

### Border Radius
- Small: 4px
- Medium: 8px
- Large: 12px
- Full: 9999px

### Shadows
- Small: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)
- Medium: 0 4px 6px rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.06)
- Large: 0 10px 15px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.05)

---

## Screen 1: Login Page

### Layout Structure
`

                                                 
              [Platform Logo/Name]               
         College Counseling Platform            
                                                 
        
                                             
      Welcome Back                           
      Sign in to access your counselors      
                                             
      [Username Input]                       
      \\domain\\username                     
                                             
      [Password Input]                       
                                     
                                             
      [Error Message Area]                   
                                             
            [Login Button]                   
                                             
      Need help? Contact Support             
                                             
        
                                                 
         2025 Counseling Platform              
                                                 

`

### Component Specifications

**Container:**
- Max-width: 400px
- Centered vertically and horizontally
- Background: White with Medium shadow
- Padding: xl (32px)
- Border-radius: Large (12px)

**Logo Section:**
- Logo icon: 64px  64px (calming icon, e.g., lotus, brain outline)
- Platform name: Heading 2, Primary Blue
- Margin-bottom: 2xl (48px)

**Welcome Text:**
- "Welcome Back": Heading 3, Neutral Gray 900
- Subtitle: Body, Neutral Gray 600
- Margin-bottom: lg (24px)

**Username Input:**
- Label: "Username", Small, Neutral Gray 700, font-weight 500
- Input field:
  - Height: 44px (minimum touch target)
  - Border: 1px solid Neutral Gray 300
  - Border-radius: Medium (8px)
  - Padding: sm (8px) md (16px)
  - Placeholder: "\\domain\\username" in Neutral Gray 400
  - Focus state: Border color Primary Blue, box-shadow small
  - Error state: Border color Error Red
- Margin-bottom: md (16px)

**Password Input:**
- Same styling as Username
- Input type: password
- Show/hide password toggle icon (eye icon) at right edge
- Margin-bottom: md (16px)

**Error Message Area:**
- Background: rgba(231, 76, 60, 0.1) (light red tint)
- Border-left: 4px solid Error Red
- Padding: sm (8px) md (16px)
- Border-radius: Small (4px)
- Text: Small, Error Red
- Icon: Alert circle icon at left
- Only visible when error present
- Margin-bottom: md (16px)

**Login Button:**
- Width: 100%
- Height: 48px
- Background: Primary Blue
- Text: Body, White, font-weight 600
- Border-radius: Medium (8px)
- Hover state: Background darkens 10%
- Active/pressed: Scale 0.98
- Loading state: Spinner icon, button disabled, opacity 0.7
- Margin-bottom: lg (24px)

**Support Link:**
- Text: Small, Primary Blue, underline on hover
- Centered alignment

**Footer:**
- Text: Caption, Neutral Gray 500
- Centered at bottom of viewport
- Margin-top: auto

### Mobile Responsive (< 640px)
- Container: Full width minus 16px margin on sides
- Padding reduced to md (16px)
- All spacing reduced by 25%

---

## Screen 2: Main Dashboard

### Layout Structure
`

 [Logo] College Counseling Platform    [Welcome, John] [Logout]

                                                               
   Choose Your Counselor                                      
   Select a category below to start your session              
                                                               
         
     [Heart Icon]        [Briefcase]         [Book]    
                                                       
     Health              Career             Academic   
     Counselor           Counselor         Counselor   
                                                       
     Mental health,      Career planning,  Study tips  
     stress mgmt...      job search...     test prep   
                                                       
    [Voice] [Video]  [Voice] [Video] [] []   
         
                                                               
         
     [Dollar Icon]       [Users Icon]      [Lightbulb] 
                                                       
     Financial           Social             Personal   
     Counselor           Counselor          Growth     
                                                       
     Budget help,        Relationships,    Goal set,   
     student loans...    social skills...  self-impr   
                                                       
    [Voice] [Video]  [Voice] [Video] [] []   
         
                                                               
      
    My Counseling Stats                                    
                                                           
      Total Sessions: 12     Total Hours: 8.5        
      Most Used: Career      Last: 2 days ago        
                                                           
                        [View All Sessions ]             
      
                                                               

  Help & Resources | Emergency Hotline: 988 | Privacy Policy  

`

### Component Specifications

**Header Navigation:**
- Background: White
- Height: 64px
- Box-shadow: Small
- Border-bottom: 1px solid Neutral Gray 200
- Padding: 0 lg (24px)
- Display: Flex, space-between, align-center

**Logo Section (Left):**
- Logo icon: 40px  40px
- Platform name: Heading 3, Primary Blue
- Clickable, returns to dashboard

**User Section (Right):**
- "Welcome, [FirstName]": Body, Neutral Gray 700
- Logout button:
  - Text: "Logout", Small, Primary Blue
  - Icon: Log-out icon
  - Padding: sm (8px) md (16px)
  - Border-radius: Medium (8px)
  - Hover: Background Neutral Gray 100

**Page Title Section:**
- "Choose Your Counselor": Heading 1, Neutral Gray 900
- Subtitle: Body, Neutral Gray 600
- Margin: xl (32px) 0 lg (24px) 0

**Counselor Category Cards:**
- Container: Grid layout
  - Desktop (>1024px): 3 columns, gap lg (24px)
  - Tablet (640-1024px): 2 columns, gap md (16px)
  - Mobile (<640px): 1 column, gap md (16px)

**Individual Card:**
- Background: White
- Border: 1px solid Neutral Gray 200
- Border-radius: Large (12px)
- Padding: lg (24px)
- Box-shadow: Small
- Hover state: Box-shadow Medium, border Primary Blue, transform translateY(-2px)
- Transition: all 0.2s ease

**Card Icon:**
- Size: 48px  48px
- Color: Primary Blue
- Background: rgba(74, 144, 226, 0.1) (light blue tint)
- Border-radius: Full (circular)
- Padding: sm (8px)
- Margin-bottom: md (16px)

**Card Title:**
- Heading 3, Neutral Gray 900
- Margin-bottom: sm (8px)

**Card Description:**
- Body, Neutral Gray 600
- Line-clamp: 2 (max 2 lines with ellipsis)
- Margin-bottom: md (16px)

**Action Buttons Row:**
- Display: Flex, gap sm (8px)
- Justify-content: space-between

**Voice Call Button:**
- Width: 48%
- Height: 40px
- Background: Primary Blue
- Text: Small, White, font-weight 600
- Icon: Microphone icon (16px) at left
- Border-radius: Medium (8px)
- Hover: Background darkens 10%
- Active: Scale 0.98

**Video Call Button:**
- Width: 48%
- Height: 40px
- Background: Secondary Green
- Text: Small, White, font-weight 600
- Icon: Video camera icon (16px) at left
- Border-radius: Medium (8px)
- Hover: Background darkens 10%
- Active: Scale 0.98

**Stats Widget:**
- Background: Gradient (Primary Blue to Secondary Green, subtle)
- Border-radius: Large (12px)
- Padding: lg (24px)
- Margin-top: 2xl (48px)
- Box-shadow: Medium

**Stats Content:**
- Title: Heading 3, White
- Stats displayed in 22 grid (desktop) or vertical (mobile)
- Each stat: Icon + Label + Value
- Text: Body, White
- Icons: 20px, White

**View All Sessions Link:**
- Text: Body, White, font-weight 600
- Icon: Arrow right (16px)
- Underline on hover
- Margin-top: md (16px)

**Footer:**
- Background: Neutral Gray 100
- Padding: md (16px)
- Text: Small, Neutral Gray 600
- Links: Primary Blue, underline on hover
- Separator: | character between links

### Mobile Responsive (< 640px)
- Header: Logo smaller (32px), username hidden, show only initials + logout icon
- Cards: Full width, reduced padding (md instead of lg)
- Stats: Stacked vertically, 2 stats per row

---

## Screen 3: Voice Session View

### Layout Structure
`

 [ Back]  Voice Session - Health Counselor     [End Session] 

                                                               
       
                               Live Transcript           
                                                         
      [Audio Waveform]         [2:34 PM] You:           
              "I've been feeling      
              really stressed..."     
                                                         
     Connected               [2:34 PM] Counselor:     
     Excellent Quality       "I understand that       
                               stress can be over-      
         whelming. Let's talk     
     [ Mute]               about what's causing     
                            this for you..."         
      Volume:                                 
                            [2:35 PM] You:           
     [End Session]          "It's mainly my          
         upcoming exams..."       
                                                         
    Session Duration:          [Auto-scroll ]          
    5:23                                                 
                                
                                  
                                                               

`

### Component Specifications

**Header Bar:**
- Background: White
- Height: 64px
- Box-shadow: Small
- Display: Flex, space-between, align-center
- Padding: 0 lg (24px)

**Back Button:**
- Icon: Arrow left (20px)
- Text: "Back", Body
- Color: Primary Blue
- Hover: Background Neutral Gray 100
- Padding: sm (8px) md (16px)
- Border-radius: Medium (8px)

**Session Title:**
- Text: "Voice Session - [Category]", Heading 3
- Color: Neutral Gray 900

**End Session Button:**
- Background: Error Red
- Text: "End Session", Body, White, font-weight 600
- Padding: sm (8px) lg (24px)
- Border-radius: Medium (8px)
- Hover: Background darkens 10%
- Icon: X icon (16px)

**Main Content Area:**
- Display: Grid, 2 columns (60% / 40% on desktop)
- Gap: lg (24px)
- Padding: xl (32px)
- Background: Neutral Gray 100

**Audio Visualization Panel (Left):**
- Background: White
- Border-radius: Large (12px)
- Padding: xl (32px)
- Box-shadow: Medium
- Display: Flex, flex-direction column, justify-content space-between
- Min-height: 600px

**Waveform Visualization:**
- Canvas or SVG element
- Height: 200px
- Width: 100%
- Animated bars responding to audio input
- Colors: Gradient from Primary Blue to Secondary Green
- Margin: 0 auto

**Connection Status Indicator:**
- Display: Flex, align-center, gap sm (8px)
- Margin-top: xl (32px)

**Status Dot:**
- Size: 12px  12px
- Border-radius: Full
- Colors:
  - Green (#27AE60): Excellent
  - Yellow (#F39C12): Fair
  - Red (#E74C3C): Poor
- Animate: Pulse effect

**Status Text:**
- "Connected": Body, Success Green
- "Excellent Quality": Small, Neutral Gray 600

**Control Panel:**
- Background: Neutral Gray 50
- Border-radius: Medium (8px)
- Padding: md (16px)
- Margin-top: lg (24px)

**Mute Button:**
- Width: 100%
- Height: 48px
- Background: White
- Border: 1px solid Neutral Gray 300
- Text: Body, Neutral Gray 700
- Icon: Microphone or microphone-off (20px)
- Border-radius: Medium (8px)
- Margin-bottom: md (16px)
- Active state (muted): Background Error Red, Text White
- Hover: Border color Primary Blue

**Volume Slider:**
- Label: "Volume", Small, Neutral Gray 700
- Slider track: Height 8px, Background Neutral Gray 200
- Slider thumb: Size 20px, Background Primary Blue
- Slider filled: Background Primary Blue
- Visual indicator: Volume bars ()
- Margin-bottom: md (16px)

**End Session Button (in controls):**
- Same as header End Session button
- Width: 100%

**Session Duration:**
- Text: "Session Duration: [MM:SS]", Small, Neutral Gray 600
- Margin-top: md (16px)
- Font-variant-numeric: tabular-nums (monospace numbers)

**Transcript Panel (Right):**
- Background: White
- Border-radius: Large (12px)
- Padding: lg (24px)
- Box-shadow: Medium
- Max-height: 600px
- Overflow-y: auto
- Custom scrollbar (thin, Primary Blue)

**Transcript Header:**
- Text: "Live Transcript", Heading 3, Neutral Gray 900
- Border-bottom: 1px solid Neutral Gray 200
- Padding-bottom: md (16px)
- Margin-bottom: md (16px)

**Transcript Messages:**
- Display: Flex, flex-direction column, gap md (16px)

**User Message:**
- Align-self: flex-start
- Max-width: 85%
- Background: Neutral Gray 100
- Padding: sm (8px) md (16px)
- Border-radius: Medium (8px)
- Border-top-left-radius: 0

**Counselor Message:**
- Align-self: flex-end
- Max-width: 85%
- Background: rgba(74, 144, 226, 0.1) (light blue tint)
- Padding: sm (8px) md (16px)
- Border-radius: Medium (8px)
- Border-top-right-radius: 0

**Message Timestamp:**
- Text: Caption, Neutral Gray 500
- Margin-bottom: 4px

**Message Speaker Label:**
- Text: Small, font-weight 600
- User: Neutral Gray 900
- Counselor: Primary Blue

**Message Text:**
- Text: Body, Neutral Gray 800
- Word-wrap: break-word

**Auto-scroll Indicator:**
- Position: Absolute, bottom right of transcript
- Background: Primary Blue
- Icon: Arrow down (16px), White
- Size: 32px  32px
- Border-radius: Full
- Box-shadow: Small
- Visible only when user scrolls up
- Click to resume auto-scroll

### Mobile Responsive (< 640px)
- Layout: Single column, transcript below audio panel
- Audio panel: Reduced height, waveform smaller
- Transcript: Fixed bottom sheet, draggable up
- Controls: Sticky at bottom
- Back button: Icon only

---

## Screen 4: Video Session View

### Layout Structure
`

 [ Back]  Video Session - Career Counselor       [End Session]     

                                                                     
        
                                         Live Transcript       
        [Avatar Video Feed]                                    
                                         [2:34 PM] You:        
     [Counselor's Avatar Face]           "I'm not sure        
           Lip-sync active               what career path      
        [Supportive expression]          to choose..."         
                                                               
     Connected   HD Quality          [2:34 PM] Counsel:    
                                         "That's a common      
         concern. Let's        
     Controls:                        explore your          
                                      interests and         
     [ Mute] [ Vol] [ Off]      strengths..."         
                                                            
        [End Session Button]          [Auto-scroll ]       
                               
                                           
    Duration: 7:45                                               
                              
                                                                     

`

### Component Specifications

**Header Bar:**
- Same as Voice Session View
- Title: "Video Session - [Category]"

**Main Content Area:**
- Display: Grid, 2 columns (70% / 30% on desktop)
- Gap: lg (24px)
- Padding: xl (32px)
- Background: Neutral Gray 900 (darker for video viewing)

**Video Container (Left):**
- Background: Black
- Border-radius: Large (12px)
- Overflow: hidden
- Aspect-ratio: 16/9
- Position: relative
- Box-shadow: Large

**Avatar Video Element:**
- Width: 100%
- Height: 100%
- Object-fit: cover
- Background: Black (while loading)

**Video Loading State:**
- Spinner: 48px, White
- Position: Absolute, centered
- Text: "Connecting to counselor...", Body, White
- Background: rgba(0, 0, 0, 0.7)

**Video Status Overlay:**
- Position: Absolute, top lg (24px), left lg (24px)
- Display: Flex, align-center, gap sm (8px)
- Background: rgba(0, 0, 0, 0.6)
- Padding: sm (8px) md (16px)
- Border-radius: Medium (8px)

**Connection Indicator:**
- Status dot: 12px, colors same as voice session
- Text: Small, White
- Quality badge: "HD" / "SD", Small, White, background rgba(255,255,255,0.2)

**Video Controls Overlay:**
- Position: Absolute, bottom 0, left 0, right 0
- Background: Linear gradient (transparent to rgba(0,0,0,0.8))
- Padding: lg (24px)
- Opacity: 0 (hidden by default)
- Hover/focus: Opacity 1, transition 0.3s
- Always visible on mobile

**Control Buttons Row:**
- Display: Flex, gap md (16px), justify-content center

**Mute Button:**
- Size: 48px  48px
- Background: rgba(255, 255, 255, 0.2)
- Icon: Microphone / microphone-off (24px), White
- Border-radius: Full
- Hover: Background rgba(255, 255, 255, 0.3)
- Active (muted): Background Error Red

**Volume Control:**
- Button: Same style as Mute
- Icon: Speaker (24px), White
- Click opens popover with volume slider above button
- Slider: Vertical, height 100px, same styling as voice session

**Camera Toggle:**
- Size: 48px  48px
- Background: rgba(255, 255, 255, 0.2)
- Icon: Video / video-off (24px), White
- Border-radius: Full
- Disabled in MVP (opacity 0.5, cursor not-allowed)
- Tooltip: "Camera feature coming soon"

**End Session Button (overlay):**
- Background: Error Red
- Text: "End Session", Body, White, font-weight 600
- Padding: sm (8px) lg (24px)
- Border-radius: Full
- Icon: X icon (20px)
- Position: Absolute, top right of controls row

**Session Duration:**
- Position: Absolute, bottom left of video
- Background: rgba(0, 0, 0, 0.6)
- Padding: 4px sm (8px)
- Border-radius: Small (4px)
- Text: Small, White
- Font-variant-numeric: tabular-nums

**Transcript Panel (Right):**
- Same as Voice Session View
- Background: White (maintains contrast with dark video area)
- All styling identical

**Quality Degradation Notice:**
- Position: Absolute, top center (below status)
- Background: Warning Yellow
- Text: Small, Neutral Gray 900
- Padding: sm (8px) md (16px)
- Border-radius: Medium (8px)
- Box-shadow: Medium
- Display: Flex, align-center, gap sm (8px)
- Icon: Alert triangle (16px)
- Message: "Video quality low. Switching to voice-only mode..."
- Animate: Slide down from top
- Auto-dismiss after 5 seconds

**Retry Video Button:**
- Appears in degradation notice
- Background: Neutral Gray 900
- Text: Small, White
- Padding: 4px sm (8px)
- Border-radius: Small (4px)
- Hover: Background Neutral Gray 700

### Mobile Responsive (< 640px)
- Layout: Single column
- Video: Full width, fixed aspect ratio
- Transcript: Collapsible drawer from bottom, 40% height when expanded
- Controls: Always visible, smaller buttons (40px)
- Pinch to zoom on video (optional enhancement)

### Tablet (640-1024px)
- Video: 65% width
- Transcript: 35% width
- All controls proportionally sized

---

## Screen 5: Session History

### Layout Structure
`

 [Logo] College Counseling Platform    [Welcome, John] [Logout]

                                                               
   My Counseling Sessions                                     
   Review your past conversations                             
                                                               
     
     Category: [All ]  Mode: [All ]  [ Date Range]    
                                  [Clear Filters]          
     
                                                               
     
     [ Health]  Dec 18, 2025  3:24 PM  15 min  []   
                                                           
     "I've been feeling really stressed about..."         
                                                 [View ]  
     
                                                               
     
     [ Career]  Dec 16, 2025  10:15 AM  22 min []   
                                                           
     "I'm not sure what career path to choose..."         
                                                 [View ]  
     
                                                               
     
     [ Academic]  Dec 14, 2025  2:45 PM  18 min []  
                                                           
     "I need help with time management for..."            
                                                 [View ]  
     
                                                               
   [ Previous]  Page 1 of 3  [Next ]                        
                                                               

`

### Component Specifications

**Header Navigation:**
- Same as Dashboard

**Page Title Section:**
- "My Counseling Sessions": Heading 1, Neutral Gray 900
- Subtitle: "Review your past conversations", Body, Neutral Gray 600
- Margin: xl (32px) 0 lg (24px) 0

**Filter Bar:**
- Background: White
- Border: 1px solid Neutral Gray 200
- Border-radius: Large (12px)
- Padding: md (16px)
- Display: Flex, gap md (16px), align-center
- Margin-bottom: lg (24px)
- Box-shadow: Small

**Category Filter Dropdown:**
- Label: "Category:", Small, font-weight 500, Neutral Gray 700
- Select element styled with custom dropdown
- Options: All, Health, Career, Academic, Financial, Social, Personal Development
- Width: 180px
- Height: 40px
- Border: 1px solid Neutral Gray 300
- Border-radius: Medium (8px)
- Padding: 0 md (16px)
- Icon: Chevron down (16px) at right
- Focus: Border color Primary Blue

**Mode Filter Dropdown:**
- Same styling as Category filter
- Options: All, Voice, Video
- Width: 140px

**Date Range Picker:**
- Button opens calendar popover
- Icon: Calendar (16px)
- Text: "Date Range" or selected range
- Width: 200px
- Height: 40px
- Border: 1px solid Neutral Gray 300
- Border-radius: Medium (8px)
- Padding: 0 md (16px)

**Clear Filters Button:**
- Background: Neutral Gray 100
- Text: "Clear Filters", Small, Neutral Gray 700
- Padding: sm (8px) md (16px)
- Border-radius: Medium (8px)
- Hover: Background Neutral Gray 200
- Icon: X icon (14px)
- Margin-left: auto

**Session List:**
- Display: Flex, flex-direction column, gap md (16px)
- Margin-bottom: lg (24px)

**Session Card:**
- Background: White
- Border: 1px solid Neutral Gray 200
- Border-radius: Large (12px)
- Padding: lg (24px)
- Box-shadow: Small
- Hover: Box-shadow Medium, border Primary Blue, cursor pointer
- Transition: all 0.2s ease

**Session Header Row:**
- Display: Flex, align-center, gap md (16px)
- Margin-bottom: sm (8px)

**Category Badge:**
- Display: Flex, align-center, gap 4px
- Icon: Category icon (20px) with background circle
- Text: Small, font-weight 600, Neutral Gray 900

**Session Metadata:**
- Display: Flex, align-center, gap sm (8px)
- Text: Small, Neutral Gray 600
- Separator: Bullet () between items
- Format: "Dec 18, 2025  3:24 PM  15 min"

**Mode Badge:**
- Icon: Microphone (voice) or Video camera (video)
- Size: 20px
- Color: Primary Blue (voice) or Secondary Green (video)
- Background: rgba color with 0.1 opacity
- Padding: 4px
- Border-radius: Small (4px)
- Margin-left: auto

**Transcript Preview:**
- Text: Body, Neutral Gray 700
- Line-clamp: 1 (single line with ellipsis)
- Font-style: italic
- Margin-bottom: sm (8px)

**View Button:**
- Position: Absolute, bottom right of card
- Text: "View", Small, Primary Blue, font-weight 600
- Icon: Arrow right (14px)
- Padding: 4px sm (8px)
- Border-radius: Small (4px)
- Hover: Background rgba(74, 144, 226, 0.1)

**Empty State:**
- Display when no sessions found
- Icon: Empty folder illustration (120px)
- Heading: "No sessions yet", Heading 3, Neutral Gray 900
- Text: "You haven't started any counseling sessions yet. Visit your dashboard to get started!", Body, Neutral Gray 600
- Button: "Go to Dashboard", Primary Blue, full styling
- Centered vertically and horizontally
- Min-height: 400px

**Pagination:**
- Display: Flex, justify-center, align-center, gap md (16px)
- Margin: lg (24px) 0

**Previous/Next Buttons:**
- Background: White
- Border: 1px solid Neutral Gray 300
- Text: Body, Neutral Gray 700
- Icon: Arrow left/right (16px)
- Padding: sm (8px) md (16px)
- Border-radius: Medium (8px)
- Hover: Border color Primary Blue, background Neutral Gray 50
- Disabled: Opacity 0.5, cursor not-allowed

**Page Indicator:**
- Text: "Page X of Y", Body, Neutral Gray 700

### Mobile Responsive (< 640px)
- Filter bar: Vertical stack, full width controls
- Session cards: Reduced padding (md), metadata wraps to multiple lines
- Mode badge: Absolute top right
- View button: Full width at bottom of card
- Pagination: Simplified to just prev/next buttons

---

## Screen 6: Session Detail / Transcript View

### Layout Structure
`

 [ Back to Sessions]         [Download] [Delete]              

                                                               
   Health Counselor Session                                   
   December 18, 2025  3:24 PM  Duration: 15 minutes  Voice 
                                                               
      
                                                           
     [2:34 PM] You:                                       
     "I've been feeling really stressed lately with       
     all my exams coming up. I can't seem to sleep        
     well and I'm constantly anxious."                    
                                                           
     [2:35 PM] Health Counselor:                          
     "I hear you, and it's completely understandable      
     to feel stressed during exam season. Many            
     students experience this. Let's talk about some      
     strategies that might help. First, can you tell      
     me about your current sleep routine?"                
                                                           
     [2:36 PM] You:                                       
     "I usually stay up until 2 or 3 AM studying,         
     then I have trouble falling asleep because I'm       
     thinking about everything I need to do."             
                                                           
     [2:37 PM] Health Counselor:                          
     "That late-night study pattern can actually          
     work against you. Your brain needs adequate rest     
     to consolidate information. Let's work on            
     establishing a healthier study schedule and          
     bedtime routine..."                                  
                                                           
     [Continue transcript...]                             
                                                           
      
                                                               
   Session Summary:                                            
   Topics Discussed: Stress management, Sleep hygiene         
   Resources Shared: None                                      
                                                               

`

### Component Specifications

**Header Navigation:**
- Background: White
- Height: 64px
- Box-shadow: Small
- Padding: 0 lg (24px)
- Display: Flex, space-between, align-center

**Back Button:**
- Icon: Arrow left (20px)
- Text: "Back to Sessions", Body, Primary Blue
- Padding: sm (8px) md (16px)
- Border-radius: Medium (8px)
- Hover: Background Neutral Gray 100

**Action Buttons (Right):**
- Display: Flex, gap sm (8px)

**Download Button:**
- Background: Primary Blue
- Text: "Download", Small, White, font-weight 600
- Icon: Download icon (16px)
- Padding: sm (8px) md (16px)
- Border-radius: Medium (8px)
- Hover: Background darkens 10%

**Delete Button:**
- Background: White
- Border: 1px solid Error Red
- Text: "Delete", Small, Error Red, font-weight 600
- Icon: Trash icon (16px)
- Padding: sm (8px) md (16px)
- Border-radius: Medium (8px)
- Hover: Background rgba(231, 76, 60, 0.1)

**Page Title Section:**
- "[Category] Counselor Session": Heading 1, Neutral Gray 900
- Margin-bottom: sm (8px)

**Session Metadata Bar:**
- Display: Flex, align-center, gap sm (8px)
- Text: Body, Neutral Gray 600
- Separator: Bullet () between items
- Icons: Calendar, clock, timer, microphone/video (16px each)
- Margin-bottom: xl (32px)

**Transcript Container:**
- Background: White
- Border: 1px solid Neutral Gray 200
- Border-radius: Large (12px)
- Padding: xl (32px)
- Box-shadow: Small
- Max-width: 800px (readable line length)
- Margin: 0 auto lg (24px) auto

**Message Blocks:**
- Display: Flex, flex-direction column, gap lg (24px)

**Individual Message:**
- Display: Grid, grid-template-columns: 80px 1fr
- Gap: md (16px)
- Padding: md (16px) 0
- Border-bottom: 1px solid Neutral Gray 100 (between messages)

**Timestamp Column:**
- Text: Caption, Neutral Gray 500
- Text-align: right
- Position: sticky, top 0 (on scroll)

**Message Content Column:**
- Display: Flex, flex-direction column, gap 4px

**Speaker Label:**
- Text: Small, font-weight 600
- User: Neutral Gray 900
- Counselor: Primary Blue
- Margin-bottom: 4px

**Message Text:**
- Text: Body, Neutral Gray 800
- Line-height: 1.6
- White-space: pre-wrap (preserves line breaks)

**Session Summary Section:**
- Background: Neutral Gray 50
- Border: 1px solid Neutral Gray 200
- Border-radius: Large (12px)
- Padding: lg (24px)
- Margin-top: xl (32px)
- Max-width: 800px
- Margin-left: auto
- Margin-right: auto

**Summary Title:**
- Text: Heading 3, Neutral Gray 900
- Margin-bottom: md (16px)

**Summary Items:**
- Display: Flex, flex-direction column, gap sm (8px)
- Label: Small, font-weight 600, Neutral Gray 700
- Value: Body, Neutral Gray 800

**Delete Confirmation Modal:**
- Overlay: Background rgba(0, 0, 0, 0.5), backdrop-blur 4px
- Modal container: Max-width 400px, centered
- Background: White
- Border-radius: Large (12px)
- Padding: xl (32px)
- Box-shadow: Large

**Modal Title:**
- Icon: Alert triangle (32px), Error Red
- Text: Heading 3, "Delete Session?", Neutral Gray 900
- Margin-bottom: md (16px)

**Modal Content:**
- Text: Body, "Are you sure you want to delete this session? This action cannot be undone.", Neutral Gray 700
- Margin-bottom: lg (24px)

**Modal Actions:**
- Display: Flex, gap md (16px), justify-content flex-end

**Cancel Button:**
- Background: White
- Border: 1px solid Neutral Gray 300
- Text: Body, Neutral Gray 700
- Padding: sm (8px) lg (24px)
- Border-radius: Medium (8px)
- Hover: Background Neutral Gray 50

**Confirm Delete Button:**
- Background: Error Red
- Text: Body, White, font-weight 600
- Padding: sm (8px) lg (24px)
- Border-radius: Medium (8px)
- Hover: Background darkens 10%

### Mobile Responsive (< 640px)
- Header: Back button icon only, action buttons smaller
- Transcript: Padding reduced to md (16px)
- Message layout: Single column, timestamp above message
- Modal: Full width minus 16px margin

---

## Screen 7: Settings / Profile (Optional Enhancement)

### Layout Structure
`

 [Logo] College Counseling Platform    [Welcome, John] [Logout]

                                                               
   Settings & Preferences                                     
                                                               
       
    Profile          Profile Information                  
    Preferences                                           
    Privacy          Username: \\vienna\\maxman123        
    Notifications    Email: [input field]                 
                     Phone: [input field]                 
                                                          
                     [Update Profile Button]              
                                                          
                     
                     Preferences                          
                                                          
                      Remember my preferred counselor    
                      Auto-save session transcripts      
                      Enable browser notifications       
                                                          
                     Default Mode: [Voice ]              
                                                          
       
                                                               

`

### Component Specifications

**Header Navigation:**
- Same as Dashboard and Session History

**Page Title:**
- "Settings & Preferences": Heading 1, Neutral Gray 900
- Margin: xl (32px) 0 lg (24px) 0

**Layout:**
- Display: Grid, 2 columns (250px sidebar + 1fr content)
- Gap: lg (24px)
- Padding: 0 xl (32px)

**Sidebar Navigation:**
- Background: White
- Border: 1px solid Neutral Gray 200
- Border-radius: Large (12px)
- Padding: md (16px)
- Position: sticky, top xl (32px)

**Nav Items:**
- Text: Body, Neutral Gray 700
- Padding: sm (8px) md (16px)
- Border-radius: Medium (8px)
- Hover: Background Neutral Gray 100
- Active: Background Primary Blue, text White
- Display: block, width 100%
- Margin-bottom: 4px

**Content Area:**
- Background: White
- Border: 1px solid Neutral Gray 200
- Border-radius: Large (12px)
- Padding: xl (32px)
- Min-height: 600px

**Section Title:**
- Heading 2, Neutral Gray 900
- Border-bottom: 1px solid Neutral Gray 200
- Padding-bottom: md (16px)
- Margin-bottom: lg (24px)

**Form Fields:**
- Label: Small, font-weight 500, Neutral Gray 700
- Input: Height 44px, border 1px solid Neutral Gray 300, border-radius Medium (8px)
- Padding: 0 md (16px)
- Margin-bottom: md (16px)
- Focus: Border color Primary Blue

**Checkbox Items:**
- Display: Flex, align-center, gap sm (8px)
- Checkbox: Size 20px, border 2px solid Neutral Gray 300, border-radius Small (4px)
- Checked: Background Primary Blue, checkmark White
- Label: Body, Neutral Gray 700
- Margin-bottom: md (16px)

**Update Button:**
- Background: Primary Blue
- Text: Body, White, font-weight 600
- Padding: sm (8px) xl (32px)
- Border-radius: Medium (8px)
- Hover: Background darkens 10%
- Margin-top: lg (24px)

### Mobile Responsive (< 640px)
- Layout: Single column, sidebar becomes tabs at top
- Tabs: Horizontal scroll, sticky
- Content: Full width

---

## Screen 8: Error States & Help

### Component Specifications

**Connection Error Screen:**
`

                                         
      [Error Icon - Wifi X symbol]       
               (64px)                    
                                         
      Connection Error                   
                                         
   We couldn't connect to the counselor. 
   Please check your internet connection 
   and try again.                        
                                         
        [Retry Connection]               
         [Back to Dashboard]             
                                         
   Need help? [Contact Support]          
                                         

`

**Error Icon:**
- Size: 64px  64px
- Color: Error Red
- Icon: Wifi-off or alert-circle
- Margin-bottom: lg (24px)

**Error Title:**
- Heading 2, Neutral Gray 900
- Margin-bottom: md (16px)

**Error Message:**
- Body, Neutral Gray 700
- Text-align: center
- Max-width: 400px
- Margin: 0 auto lg (24px) auto

**Action Buttons:**
- Primary: "Retry Connection", full Primary Blue styling
- Secondary: "Back to Dashboard", border button styling
- Stack vertically on mobile
- Gap: md (16px)

**Emergency Banner (Crisis Detection):**
`

   Emergency Resources Available               
                                                 
 If you're in crisis, help is available 24/7:   
                                                 
  National Suicide Prevention Lifeline: 988   
  [Call Now]     [Chat Online]              
                                                 
                                    [Dismiss ]  

`

**Banner:**
- Background: rgba(239, 71, 67, 0.1) (light red)
- Border: 2px solid Error Red
- Border-radius: Large (12px)
- Padding: lg (24px)
- Position: Fixed, top 80px (below header)
- Z-index: 1000
- Box-shadow: Large
- Width: 90%, max-width 600px
- Left: 50%, transform translateX(-50%)

**Banner Icon:**
- Warning triangle, Error Red, 24px
- Float left

**Banner Text:**
- Heading 3, Neutral Gray 900
- Body text, Neutral Gray 800
- Hotline number: Heading 2, Error Red, font-weight 700

**Action Buttons:**
- "Call Now": Background Error Red, text White
- "Chat Online": Border button with Error Red
- Display inline, gap md (16px)

**Dismiss Button:**
- Position: Absolute, top right
- Icon: X (20px), Neutral Gray 600
- Padding: sm (8px)
- Hover: Background rgba(0,0,0,0.05)

---

## Accessibility Annotations

**All Interactive Elements:**
- Minimum touch target: 44px  44px
- Focus indicators: 2px solid Primary Blue, 2px offset
- Focus order: Logical tab sequence
- Skip links: "Skip to main content" hidden until focused

**Color Contrast:**
- Text on backgrounds: Minimum 4.5:1
- UI components: Minimum 3:1
- Verify all combinations pass WCAG AA

**ARIA Labels:**
- Buttons: aria-label describing action
- Form inputs: Proper label associations
- Status messages: aria-live regions
- Modal dialogs: aria-modal, aria-labelledby, aria-describedby

**Keyboard Navigation:**
- Tab: Forward navigation
- Shift+Tab: Backward navigation
- Enter/Space: Activate buttons
- Escape: Close modals/overlays
- Arrow keys: Navigate lists, sliders

**Screen Reader Announcements:**
- Page title updates on navigation
- Loading states announced
- Error messages announced immediately
- Success confirmations announced

---

## Animation & Transitions

**Page Transitions:**
- Duration: 200ms
- Easing: cubic-bezier(0.4, 0, 0.2, 1)
- Fade in/out: opacity 0 to 1

**Hover States:**
- Duration: 150ms
- Easing: ease-in-out
- Properties: background-color, border-color, transform

**Modal Overlays:**
- Backdrop: Fade in 300ms
- Content: Scale from 0.95 to 1.0, 300ms
- Exit: Reverse animation

**Loading Spinners:**
- Rotation: 1s linear infinite
- Size: 24px (inline), 48px (full screen)

**Toast Notifications:**
- Enter: Slide in from right, 300ms
- Exit: Fade out, 200ms
- Auto-dismiss: 5 seconds

**Connection Status:**
- Status dot: Pulse animation 2s infinite
- Quality change: Smooth color transition 500ms

---

## Component Library Mapping (shadcn/ui)

**Components to Use:**
- Button: All buttons
- Card: Counselor cards, session cards, stats widget
- Form: Login form, settings forms
- Input: Text inputs, password inputs
- Select: Dropdown filters
- Dialog: Delete confirmation, error modals
- Toast: Notifications, status messages
- Avatar: User profile icon
- Badge: Category badges, status indicators
- Slider: Volume controls
- Switch: Toggle settings
- Tabs: Settings navigation (mobile)

**Custom Components to Build:**
- AudioWaveform: SVG/Canvas visualization
- VideoPlayer: HTML5 video with custom controls
- TranscriptPanel: Custom message layout
- ConnectionIndicator: Status dot with quality badge

---

## Design Handoff Notes

**Assets Needed:**
- Platform logo (SVG, multiple sizes)
- Counselor category icons (6+, SVG, 48px)
- Empty state illustrations
- Loading spinner animation
- Error state illustrations

**Fonts:**
- Inter (Regular 400, Medium 500, Semibold 600, Bold 700)
- Variable font preferred for better rendering

**Export Specifications:**
- SVG icons: 24px grid, 2px stroke, optimize for web
- Images: 2x resolution for retina displays
- Shadows: CSS box-shadow values provided

**Developer Notes:**
- Use CSS custom properties for colors
- Implement dark mode considerations (future)
- Ensure components are composable/reusable
- Test on real devices, not just emulators

---

**End of Wireframe Specifications**
**Ready for Design Implementation**

