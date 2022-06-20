# lineup-generator
A program that outputs optimal lineups for my summer league swim meets given time/age data on a group of swimmers.

OVERVIEW:
This project seeks to write optimal lineups for swim meets for my summer league swim team.

A lineup is a table detailing which swimmers swim what events. My goal is to automate writing
optimal lineups so we can ideally have the best swimmers in the events that maximize their
output. This is a task that normally takes a few hours when done by hand.

The program requires that each swimmer have times recorded for each of the 4 strokes and their ages.
It is built to take in data in the way that it has always been kept at our summer swim club:
A database of only boys or girls, not separated by age group.
Therefore, to write lineups for the whole meet, this whole process has to be run twice.
The data should be in the following format (csv):

Name,Fly,Back,Breast,Free,Age

There are 3 classes:
- DataManager contains functions for unique data manipulations required to do relay optimizations - this is just for organizational
reasons -- although these functions could be in RelayGenerator, it is far easier to understand and process this way in my opinion
- RelayGenerator writes relays
- LineupGenerator writes individual events and finishes the lineup

HOW TO USE:
Simply type python LineupGenerator.py <filepath to csv file containing data> <number of lanes> 
and it will print out the resulting lineups.
Number of lanes is how many lanes are provided to your swimmers at a meet--can be either 2 or 3
A sample (falsified) dataset is provided for testing (swimmer_df.csv)

TECHNICAL DETAILS:

Each meet has 2 relays: one medley relay and one freestyle relay. The medley includes one swimmer in each stroke,
while the freestyle has 4 swimmers that all swim freestyle. For every event, there is a boys and girls event, so there are
4 total events that are relays, each with 4 swimmers. For each relay, the ages of all 4 swimmers must sum to be less than 
52. 

In addition to the relays, there are 40 individual events. These individual events are:
- Each age group (5 age groups) swims one event of each stroke (4 strokes) and there are both boy and girls versions of each event
(2 of each) --> 5 x 4 x 2 accounts for the other 40 events.

The restraints on the swimmers are as follows:
- There must be 4 total relays: a girls medley, a boys medley, a girls freestyle, and a boys freestyle
- Each individual event must have exactly 2 swimmers participating in it (provided there are enough total swimmers for that)
- Each swimmer can be in up to 4 events maximum, but they cannot be all individual events -- that is, a swimmer
can be in up to 3 individual events and can be in both relays, but not both of those things, as that would be 5 total events.

Relays are worth more points than individual events, so I chose to create relays first, and then build individual
events around them. 

The relays are created in the RelayGenerator class. I use Scipy minimization to do these, optimizing for total time (trying to
minimize time) while meeting the age requirement. I do this by creating the relays as a list of 1's and 0's, where 1 represents 
the corresponding swimmer swimming the event while 0 means they are not. The dot product of this with a list of the ages (provided
everything is still in order) should be less than 52 -- this is the constraint passed into the minimization function.

After the relays are generated, they are manipulated into a dictionary that maps from a swimmer name to a 1 or 0 depending on if
they are swimming it. This is passed into the LineupGenerator class.

The LineupGenerator class contains a dictionary that maps from swimmer names to how many events they are swimming, and it
begins by adding in the relay data. It then starts to write in the individual events. Note that this algorithm is run on each
age group and each gender, so all swimmers are considered equally viable for a given event. 
The algorithm by which it writes lineups is as follows:
- Since some strokes are slower naturally than others, it normalizes all swimmers times by dividing them by the fastest time in
their event. This means a time of 1 is the fastest (best) time, and a very low time is the slowest (worst) time
- It then goes through each event and sorts the list of swimmers from best to worst in that event
- It takes the top 2 in each event and marks them as those swimming the event
- If any swimmer is in too many events, it finds their worst stroke (with the lowest "time score") and takes them out of it,
moving the next person up into the event
- It continues to perform this operation until the lineup is legal
- All swimmers in each event who are not marked as swimming it are now trimmed off

After it writes this lineup, it has a dictionary mapping from each event to the swimmers who are swimming it. 
At this point, we have all of the information we need, but this is not how the children are used to seeing their lineups 
written out, so we have a somewhat cumbersome pandas-based function to write it into an understandable form.

All of these pieces fit together in the following way:
- The RelayGenerator creates the relays
- The database of swimmers is split up by age group
- A LineupGenerator for each age group is created and writes the lineups 

At this point, the lineups are as complete as they can be, so they are printed out -- although in practice I would have them written
to an excel sheet.
