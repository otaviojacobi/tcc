package web;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLConnection;
import java.net.URLEncoder;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;

/**
 * PTSP-Competition
 * Created by Diego Perez, University of Essex.
 * Date: 17/02/12
 */
public class UploaderExample
{

    public void upload(String username, String filename, int a_waypointsCollected, int a_time, ArrayList<Integer> a_moves) throws Exception
    {
        try {

            int totalDataSize = a_moves.size();
            int chunkSize = 1000;
            int remainingData = totalDataSize;
            int totalSent = 0;
            while(remainingData > 0)
            {
                int toBeSent = (remainingData < chunkSize)? remainingData : chunkSize;

                // Construct data
                String dataStr = URLEncoder.encode("username", "UTF-8") + "=" + URLEncoder.encode(username, "UTF-8");
                dataStr += "&" +  URLEncoder.encode("filename", "UTF-8") + "=" + URLEncoder.encode(filename, "UTF-8");
                dataStr += "&" +  URLEncoder.encode("waypoints", "UTF-8") + "=" + URLEncoder.encode(a_waypointsCollected+"", "UTF-8");
                dataStr += "&" +  URLEncoder.encode("time", "UTF-8") + "=" + URLEncoder.encode(a_time+"", "UTF-8");
                dataStr += "&" +  URLEncoder.encode("chunkLength", "UTF-8") + "=" + URLEncoder.encode(toBeSent+"", "UTF-8");
                if(totalSent == 0)
                    dataStr += "&" +  URLEncoder.encode("append", "UTF-8") + "=" + URLEncoder.encode("0", "UTF-8");
                else
                    dataStr += "&" +  URLEncoder.encode("append", "UTF-8") + "=" + URLEncoder.encode("1", "UTF-8");

                StringBuilder chunkStr = new StringBuilder();
                for(int i = 0; i < toBeSent; ++i)
                {
                    int pos = totalSent + i;
                    chunkStr.append(a_moves.get(pos) + "");
                }
                dataStr += "&" +  URLEncoder.encode("actions", "UTF-8") + "=" + URLEncoder.encode(chunkStr.toString()+"", "UTF-8");

                // Send data
                URL url = new URL("http://cseepgdp2.essex.ac.uk/upload_action_file.php?c=cig12");
                URLConnection conn = url.openConnection();
                conn.setDoOutput(true);
                OutputStreamWriter wr = new OutputStreamWriter(conn.getOutputStream());
                wr.write(dataStr);
                wr.flush();

                // Wait until we get the response
                BufferedReader rd = new BufferedReader(new InputStreamReader(conn.getInputStream()));
                String line;
                StringBuilder response = new StringBuilder();
                while ((line = rd.readLine()) != null) {
                    response.append(line.trim());
                }
                //System.out.println(response.toString());
                //System.out.println("---------------------------------------------------");
                wr.close();
                rd.close();


                totalSent += toBeSent;
                remainingData -= toBeSent;
            }

        } catch (Exception e) {
            e.printStackTrace();
        }

    }

}

