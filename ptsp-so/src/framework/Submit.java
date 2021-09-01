package framework;

import framework.core.Exec;
import framework.core.Game;
import framework.core.PTSPConstants;
import framework.core.PTSPView;
import framework.sec.ChiefOfPolice;
import framework.utils.JEasyFrame;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.PrintWriter;

/**
 * PTSP-Competition
 * Created by Diego Perez, University of Essex.
 * Date: 19/12/11
 */
public class Submit extends Exec
{
    private static boolean m_starting = true;

    private static String saveLog(String fileRoute, String toWrite)
    {
        try{

            PrintWriter pw = new PrintWriter(new BufferedWriter(new FileWriter(fileRoute, !m_starting)));
            pw.println(toWrite);
            pw.close();
            m_starting = false;

        }catch(Exception e)
        {
            e.printStackTrace();
        }

        return null;
    }



    public static void main(String[] args)
    {
        String routeBase = "/home/diego/ptspLeagueSubmission/";
        String route = "/home/diego/ptspLeagueSubmission/";
        int mapIds[];
        String maps[];
        int[][] records;

        m_visibility = false; //Set here if the graphics must be displayed or not (for those modes where graphics are allowed).
        m_writeOutput = false; //Indicate if the actions must be saved to a file after the end of the game.


        try
        {
            Game game;
            ChiefOfPolice.start();

            if(args.length < 5)
            {
                printUsage();
            }
            else
            {
                //Get the params
                String controllerName = args[0];
                int mapTimes = Integer.parseInt(args[1]);
                String stage = args[2];
                String username = args[3];
                int runID = Integer.parseInt(args[4]);


                route += username +  "/" + stage + "/maps/Stage";
                //String routeLog = route + username + "/" + username + ".txt";
                String routeLog = "/home/diego/log/" + username + ".txt";
                String routeProgressLog = "/home/diego/log/" + username + "_progress.txt";

                int numMaps = 20;
                route = "/home/diego/ptspLeagueSubmission/" + username +  "/Z/maps/Stage";

                //Get the maps
                maps = new String[numMaps];
                mapIds = new int[numMaps];
                for(int i=5; i<numMaps+5; ++i)
                {
                    mapIds[i-5] = Integer.parseInt(args[i]);
                    if(mapIds[i-5] < 10)
                        maps[i-5] = "ptsp_league_map0"+mapIds[i-5]+".map";
                    else
                        maps[i-5] = "ptsp_league_map"+mapIds[i-5]+".map";
                }

                //Get the records
                records = new int[numMaps][2];
                int mapIdx = 0;
                for(int i = numMaps+5; i < args.length; i+=2)
                {
                    records[mapIdx][0] = Integer.parseInt(args[i]);
                    records[mapIdx][1] = Integer.parseInt(args[i+1]);

                    mapIdx++;
                }

                m_mapNames = new String[maps.length];
                for(int i = 0; i < maps.length; ++i)
                {
                    String mapName = route + stage + "/" + maps[i];
                    m_mapNames[i] = mapName;
                }

                //Stores the results of all the executions
                m_controllerName = controllerName;
                int results[][][] = new int[maps.length][mapTimes][2];
                double average[][] = new double [maps.length][2];
                for(int i = 0; i < maps.length; ++i)
                {
                    for(int j = 0; j < mapTimes; ++j)
                    {
                        //runGameTimed(false);
                        //runGameTimedSpeedOptimised(false,false);
                        runGame(false,0);

                        saveLog(routeLog, "Executing " + controllerName + " in map " + m_mapNames[i] + " (" + j + "):" +
                                "   ... result: " + m_game.getWaypointsVisited() + " waypoints in " + m_game.getTotalTime());

                        int gameWaypoints = m_game.getWaypointsVisited();
                        int gameTotalTime = m_game.getTotalTime();

                        if(username.equalsIgnoreCase("diego_test"))
                        {
                            String filename = mapIds[i] + "_" + runID + "_" + gameWaypoints + "_" + gameTotalTime + ".txt";
                            String bestRoute = routeBase + "allRoutes/";

                            saveLog(routeLog, "Saving match replay to: " + bestRoute+filename);

                            m_game.saveRoute(bestRoute+filename);

                        }else
                        if(username != "diego")
                        {
                            saveLog(routeLog, "Checking gameWaypoints > records[i][0] with i = " + i + " and gameWaypoints = " + gameWaypoints +
                                    " and records[i][0]= " + records[i][0] + " gameTotalTime = " + gameTotalTime + " and records[i][1] = " + records[i][1]);

                            if(gameWaypoints > records[i][0] || (gameWaypoints == records[i][0] && gameTotalTime < records[i][1]))
                            {
                                String filename = gameWaypoints + "_" + gameTotalTime + "_" + username +".txt";
                                String bestRoute = routeBase + "bestRoutes/" + mapIds[i] + "/";

                                //NEW RECORD!!
                                m_game.saveRoute(bestRoute+filename);

                                //saveLog(routeLog, "New RECORD saved: " + bestRoute+filename);
                            }
                        }

                        results[i][j][0] = gameWaypoints;
                        results[i][j][1] = gameTotalTime;

                        average[i][0] += results[i][j][0];
                        average[i][1] += results[i][j][1];


                        try
                        {
                            FileWriter fw = new FileWriter(routeProgressLog,true);
                            fw.write(stage);
                            fw.close();
                        }catch(Exception e){
                            saveLog(routeLog, "File write error: " + e.toString());
                        }
                    }

                    m_game.advanceMap();

                    average[i][0] /= mapTimes;
                    average[i][1] /= mapTimes;
                }

                //Print results

                System.out.print("L1-MAPS:");
                for(int i = 0; i < mapIds.length; ++i)
                {
                    for(int j = 0; j < mapTimes; ++j)
                    {
                        System.out.print(mapIds[i] + ",");
                    }
                }
                System.out.println();

                System.out.print("L2-WAYPOINTS:");
                for(int i = 0; i < maps.length; ++i)
                {
                    for(int j = 0; j < mapTimes; ++j)
                    {
                        System.out.print(results[i][j][0] + ",");
                    }
                }
                System.out.println();

                System.out.print("L3-TIME:");
                for(int i = 0; i < maps.length; ++i)
                {
                    for(int j = 0; j < mapTimes; ++j)
                    {
                        System.out.print(results[i][j][1] + ",");
                    }
                }
                System.out.println();


                System.out.print("L4-AVG_WAYPOINTS:");
                for(int i = 0; i < maps.length; ++i)
                {
                    System.out.print(average[i][0] + ",");
                }
                System.out.println();

                System.out.print("L5-AVG_TIME:");
                for(int i = 0; i < maps.length; ++i)
                {
                    System.out.print(average[i][1] + ",");
                }
                System.out.println();

            }

        }catch(Exception e)
        {
            e.printStackTrace();
        }

    }

    /**
     * Run a game in : the game executes ONE map.
     *
     * @param visual Indicates whether or not to use visuals
     * @param delay Includes delay between game steps.
     */
    public static void runGame(boolean visual, int delay)
    {
        //Get the game ready.
        if(!prepareGame())
            return;

        //Indicate what are we running
        if(m_verbose) System.out.println("Running " + m_controllerName + " in map " + m_game.getMap().getFilename() + "...");

        JEasyFrame frame;
        if(visual)
        {
            //View of the game, if applicable.
            m_view = new PTSPView(m_game, m_game.getMapSize(), m_game.getMap(), m_game.getShip(), m_controller);
            frame = new JEasyFrame(m_view, "PTSP-Game: " + m_controllerName);
        }


        while(!m_game.isEnded())
        {
            //When the result is expected:
            long then = System.currentTimeMillis();
            long due = then + PTSPConstants.ACTION_TIME_MS;

            //Advance the game.
            int actionToExecute = m_controller.getAction(m_game.getCopy(), due);

            //Exceeded time
            long now = System.currentTimeMillis();
            long spent = now - then;

            if(spent > PTSPConstants.TIME_ACTION_DISQ)
            {
                actionToExecute = 0;
                System.out.println("Controller disqualified. Time exceeded: " + (spent - PTSPConstants.TIME_ACTION_DISQ));
                m_game.abort();

            }else{

                if(spent > PTSPConstants.ACTION_TIME_MS)
                    actionToExecute = 0;
                m_game.tick(actionToExecute);
            }

            int remaining = (int) Math.max(0, delay - (now-then));//To adjust to the proper framerate.
            //Wait until de next cycle.
            waitStep(remaining);

            //And paint everything.
            if(m_visibility)
            {
                m_view.repaint();
                if(m_game.getTotalTime() == 1)
                    waitStep(m_warmUpTime);
            }
        }

        if(m_verbose)
            m_game.printResults();

        //And save the route, if requested:
        if(m_writeOutput)
            m_game.saveRoute();

    }

    public static void printUsage()
    {
        System.out.println("Error, incorrect number of arguments. Usage:");
        System.out.println(" java Submit <controllerName> <numExecs> <stage> <username> m0 m1 m2 m3 ...");
        System.out.println(" where: ");
        System.out.println("   <controllerName>   Mandatory field. Indicates the full path to the controller (example: 'controllers.greedy.SubmissionTestController').");
        System.out.println("   <numExecs>         Mandatory field, indicates how many times each map has to be executed.");
        System.out.println("   <stage>            Mandatory field, indicates the stage where the maps are.");
        System.out.println("   <username>         Mandatory field, indicates the username.");
        System.out.println("   m0 m1 m2 m3 m4 ...    Maps to execute in (map_id).");
        System.out.println(" example: ");
        System.out.println("    java Submit controllers.greedy.SubmissionTestController 5 A diego ptsp_map01.map ptsp_map02.map");
    }



}
