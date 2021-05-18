import React, { useEffect, useRef, useState } from 'react';
import { AgGridColumn, AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/dist/styles/ag-grid.css';
import 'ag-grid-community/dist/styles/ag-theme-material.css';
import { Backdrop, Button, CircularProgress, Divider, FormControl, Grid, IconButton, Snackbar, TextField } from '@material-ui/core';
import CloseIcon from '@material-ui/icons/Close';
import RestoreIcon from '@material-ui/icons/Restore';
import DeleteIcon from '@material-ui/icons/Delete';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({
    close: {
      padding: theme.spacing(0.5),
    },
    backdrop: {
        zIndex: theme.zIndex.drawer + 1,
        color: '#fff',
    },
}));

const Subscriptions = props => {
    const classes = useStyles();
    /**
     * "email": "shivasye92@gmail.com",
        "district_id": 276,
        "state_id": 16,
        "active": true,
        "state_name": "Karnataka",
        "district_name": "Bangalore Rural"
    */
    const [email, setEmail] = useState('');
    const gridRef = useRef();
    const [rowData, setRowData] = useState([]);
    const [backdrop, setBackdrop] = useState(false);
    const [message, setMessage] = useState({
        open: false,
        msg: ''
    });
    
    
    const handleMessageClose = (event, reason) => {
        if (reason === 'clickaway') {
            return;
        }
        setMessage({open: false, msg: ''});
    }
    const onEmailChange = e => {
        setEmail(e.target.value);
    }

    const searchSubscriptions = async () => {
        try {
            setBackdrop(true);
            if (email) {
                const { subscriptions } = await fetch(`/v2/subscriptions?email=${encodeURIComponent(email)}`, {
                    method: "GET",
                }).then(res => res.json());
                setRowData(subscriptions);
            } else {
                setMessage({
                    open: true,
                    msg: 'Email ID is required'
                })
            }
        } catch (error) {
            console.error(error);
            setMessage({
                open: true,
                msg: 'Exception Occurred, please contact administrator',
            });
        } finally {
            setBackdrop(false);
        }
    }

    const onDeleteSubscription = async (params) => {
        try {
            setBackdrop(true);
            const subsList = [{...params.data}];
            let url = '/v2/subscribe';
            if (params.data.search_type === 'PINCD'){
                url = '/v2/pincode/subscribe';
            }
            const delResp = await fetch(url, {
                method: "DELETE",
                body: JSON.stringify(subsList)
            }).then(res => res.json());
            if (!delResp.isError) {
                setMessage({
                    open: true,
                    msg: 'Successfully deleted the subscription'
                });
            } else {
                throw new Error("Error occurred in deletion");
            }
        } catch (error) {
            console.error(error);
            setMessage({
                open: true,
                msg: error.message ? error.message : "Exception occurred"
            });
        } finally {
            setBackdrop(false);
            await searchSubscriptions();
        }
    }

    return <>
    <Snackbar
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        open={message.open}
        autoHideDuration={6000}
        onClose={handleMessageClose}
        message={message.msg}
        action={
          <>
            <IconButton aria-label="close" color="inherit"
              className={classes.close} onClick={handleMessageClose}
            >
              <CloseIcon />
            </IconButton>
          </>
        }
    />
    <Backdrop className={classes.backdrop} open={backdrop}>
        <CircularProgress color="inherit" />
    </Backdrop>
    <Grid container item xs={12} sm={12} md={12} direction='row'>
        <Grid item xs={2} sm={2} md={2}>
            <FormControl variant="standard" style={{paddingLeft: 8}} >
                <TextField id="full-width-email"
                    placeholder="Enter your email ID"
                    fullWidth 
                    margin="normal"
                    InputLabelProps={{
                        shrink: true,
                    }}
                    variant="standard" type='email' value={email}
                    onChange={onEmailChange}
                />
            </FormControl>
        </Grid>
        <Grid item alignSelf='center'>
            <Button variant="contained" color="primary" style={{ paddingLeft: 8 }}
                onClick={searchSubscriptions}
            >
                Search
            </Button>
        </Grid>
    </Grid>
    <Grid container item xs={12} sm={12} md={12} direction='row'>

        <Grid item xs={7} md={7} sm={7}>
            <div className="ag-theme-material" style={{ height: 400 }}>
                <AgGridReact ref={gridRef} rowData={rowData.filter(d => d.search_type !== "PINCD")} >
                    {/* <AgGridColumn field="email" headerName='Email' sortable={ true } filter={ true }></AgGridColumn> */}
                    <AgGridColumn field="state_name" headerName='State' sortable={ true } filter={ true }></AgGridColumn>
                    <AgGridColumn field="district_name" headerName='District' sortable={ true } filter={ true }></AgGridColumn>
                    <AgGridColumn field="active" headerName='Subscription Status' sortable={ true } filter={ true }
                        cellRendererFramework={params => {
                            return <IconButton onClick={() => onDeleteSubscription(params)}>
                                <DeleteIcon />
                            </IconButton>
                        }}></AgGridColumn>
                </AgGridReact>
            </div>

        </Grid>
        <Divider orientation="vertical" flexItem />
        <Grid item xs={4} md={4} sm={4}>
            <div className="ag-theme-material" style={{ height: 400 }}>
                <AgGridReact ref={gridRef} rowData={rowData.filter(d => d.search_type === "PINCD")} >
                    {/* <AgGridColumn field="email" headerName='Email' sortable={ true } filter={ true }></AgGridColumn> */}
                    <AgGridColumn field="pincode" headerName='Pincode' sortable={ true } filter={ true }></AgGridColumn>
                    <AgGridColumn field="active" headerName='Subscription Status' sortable={ true } filter={ true }
                        cellRendererFramework={params => {
                            return <IconButton onClick={() => onDeleteSubscription(params)}>
                                <DeleteIcon />
                            </IconButton>
                        }}></AgGridColumn>
                </AgGridReact>
            </div>

        </Grid>
    </Grid>
    </>
}

export default Subscriptions;