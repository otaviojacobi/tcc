package framework;

import controllers.keycontroller.KeyController;
import framework.core.*;
import framework.utils.JEasyFrame;

import java.awt.*;

/**
 * This class may be used to execute the game in timed or un-timed modes, with or without
 * visuals. Competitors should implement his controller in a subpackage of 'controllers'.
 * The skeleton classes are already provided. The package
 * structure should not be changed (although you may create sub-packages in these packages).
 */
@SuppressWarnings("unused")
public class ExecAsync extends Exec
{

    /**
     * Run the game with time limit (asynchronous mode). This is how it will be done in the competition and submission.
     * Can be played with and without visual display of the game.
     *
     * @param visual Indicates whether or not to use visuals
     */
    public static void runOneGameTimed(boolean visual)
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

            //If we are going to play the game with the cursor keys, add the listener for that.
            if(m_controller instanceof KeyController)
            {
                frame.addKeyListener(((KeyController)m_controller).getInput());
            }
        }

        //Start the controller in a separated thread.
        Thread thr = new Thread(m_controller);
        thr.start();

        while(!m_game.isEnded() && thr.isAlive())
        {
            //When the result is expected:
            long due = System.currentTimeMillis()+PTSPConstants.ACTION_TIME_MS;

            //Supply the game copy and the expected time
            m_controller.update(m_game.getCopy(),due);

            //Wait until de next cycle.
            waitStep(PTSPConstants.ACTION_TIME_MS);

            //Advance the game
            m_game.tick(m_controller.getMove());

            //And paint everything.
            if(visual)
            {
                m_view.repaint();
            }
        }

        //Print the game results.
        if(m_verbose)
            m_game.printResults();

        //And save the route, if requested:
        if(m_writeOutput)
            m_game.saveRoute();

        //Finish the controller.
        m_controller.terminate();
    }

    /**
     * Run the game with time limit (asynchronous mode). This is how it will be done in the competition and submission.
     * It executes several times, in several maps, without visuals, in an optimised mode.
     *
     * @param trials The number of trials to be executed
     */
    public static void runGamesTimedOptimised(int trials)
    {
        //Prepare the average results.
        double avgTotalWaypoints=0;
        double avgTotalTimeSpent=0;
        int totalDisqualifications=0;
        int totalNumGamesPlayed=0;
        boolean moreMaps = true;

        for(int m = 0; moreMaps && m < m_mapNames.length; ++m)
        {
            String mapName = m_mapNames[m];
            double avgWaypoints=0;
            double avgTimeSpent=0;
            int numGamesPlayed = 0;

            if(m_verbose)
            {
                System.out.println("--------");
                System.out.println("Running " + m_controllerName + " in map " + mapName + "...");
            }

            //For each trial...
            for(int i=0;i<trials;i++)
            {
                // ... create a new game.
                if(!prepareGame())
                    continue;
                
                numGamesPlayed++; //another game

                //Start the controller in a separated thread.
                Thread thr = new Thread(m_controller);
                thr.start();


                while(!m_game.isEnded() && thr.isAlive())
                {
                    //When the result is expected:
                    long due = System.currentTimeMillis()+PTSPConstants.ACTION_TIME_MS;

                    //Supply the game copy and the expected time
                    m_controller.update(m_game.getCopy(),due);

                    int waited=PTSPConstants.ACTION_TIME_MS/PTSPConstants.INTERVAL_WAIT;

                    for(int j=0;j<PTSPConstants.ACTION_TIME_MS/PTSPConstants.INTERVAL_WAIT;j++)
                    {
                        waitStep(PTSPConstants.INTERVAL_WAIT);

                        if(m_controller.hasComputed())
                        {
                            waited=j;
                            break;
                        }
                    }

                    //Advance the game
                    m_game.tick(m_controller.getMove());
                }


                //Update the averages with the results of this trial.
                avgWaypoints += m_game.getWaypointsVisited();
                avgTimeSpent += m_game.getTotalTime();

                //Print the results.
                if(m_verbose)
                {
                    System.out.print(i+"\t");
                    m_game.printResults();
                }

                //And save the route, if requested:
                if(m_writeOutput)
                    m_game.saveRoute();

                //Finish the controller.
                m_controller.terminate();
            }

            moreMaps = m_game.advanceMap();

            avgTotalWaypoints += (avgWaypoints / numGamesPlayed);
            avgTotalTimeSpent += (avgTimeSpent / numGamesPlayed);
            totalDisqualifications += (trials - numGamesPlayed);
            totalNumGamesPlayed += numGamesPlayed;

            //Print the average score.
            if(m_verbose)
            {
                System.out.println("--------");
                System.out.format("Average waypoints: %.3f, average time spent: %.3f\n", (avgWaypoints / numGamesPlayed), (avgTimeSpent / numGamesPlayed));
                System.out.println("Disqualifications: " + (trials - numGamesPlayed) + "/" + trials);
            }
        }

        //Print the average score.
        if(m_verbose)
        {
            System.out.println("-------- Final score --------");
            System.out.format("Average waypoints: %.3f, average time spent: %.3f\n", (avgTotalWaypoints / m_mapNames.length), (avgTotalTimeSpent / m_mapNames.length));
            System.out.println("Disqualifications: " + (trials*m_mapNames.length - totalNumGamesPlayed) + "/" + trials*m_mapNames.length);
        }
    }


    /**
     * Run the game in asynchronous mode but proceed as soon as the controllers reply. The time limit still applies so
     * so the game will proceed after 40ms regardless of whether the controller managed to calculate a turn.
     *
     * @param visual Indicates whether or not to use visuals
     */
    public static void runGameTimedSpeedOptimised(boolean visual)
    {

        int wait = PTSPConstants.INTERVAL_WAIT;
        if(visual)
            wait = 5;

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

        //Start the controller in a separated thread.
        Thread thr = new Thread(m_controller);
        thr.start();


        while(!m_game.isEnded() && thr.isAlive())
        {
            //When the result is expected:
            long due = System.currentTimeMillis()+PTSPConstants.ACTION_TIME_MS;

            //Supply the game copy and the expected time
            m_controller.update(m_game.getCopy(),due);

            int waited=PTSPConstants.ACTION_TIME_MS/wait;

            for(int j=0;j<PTSPConstants.ACTION_TIME_MS/wait;j++)
            {
                waitStep(wait);

                if(m_controller.hasComputed())
                {
                    waited=j;
                    break;
                }
            }

            //Advance the game
            m_game.tick(m_controller.getMove());

            //And paint everything.
            if(visual)
            {
                m_view.repaint();
            }
        }

        //Print results.
        if(m_verbose)
            m_game.printResults();

        //And save the route, if requested:
        if(m_writeOutput)
            m_game.saveRoute();

        //Finish the controller.
        m_controller.terminate();
    }


    /**
     * The main method. Several options are listed - simply remove comments to use the option you want.
     *
     * @param args the command line arguments. Not needed in this class.
     */
    public static void main(String[] args)
    {
        m_mapNames = new String[]{"maps/StageA/ptsp_map01.map", "maps/StageA/ptsp_map02.map"};  //Set here the name of the map to play in.
        m_controllerName = "controllers.greedy.GreedyController"; //Set here the controller name. Leave it to null to play with KeyController.
        m_controllerName = "controllers.random.RandomController";
        m_visibility = true; //Set here if the graphics must be displayed or not (for those modes where graphics are allowed).
        m_writeOutput = false; //Indicate if the actions must be saved to a file after the end of the game.
        m_verbose = true;

        /////// 1. Runs in the competition mode, in ONE MAP, waiting 40ms for each action.
        runOneGameTimed(m_visibility);

        /////// 2. Runs in the competition mode, in ONE MAP, but advancing as soon as the controller is ready -> Much quicker!
        //runGameTimedSpeedOptimised(m_visibility);

        /////// 3. It executes numTrials times, in several maps, without visuals, in an optimised mode.
        //int numTrials=5;
        //runGamesTimedOptimised(numTrials);
    }


}