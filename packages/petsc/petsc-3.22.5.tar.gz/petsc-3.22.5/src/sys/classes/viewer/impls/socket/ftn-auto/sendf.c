#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* send.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscviewer.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscopensocket_ PETSCOPENSOCKET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscopensocket_ petscopensocket
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewersocketopen_ PETSCVIEWERSOCKETOPEN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewersocketopen_ petscviewersocketopen
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewersocketsetconnection_ PETSCVIEWERSOCKETSETCONNECTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewersocketsetconnection_ petscviewersocketsetconnection
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscopensocket_( char hostname[],int *portnum,int *t, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
/* insert Fortran-to-C conversion for hostname */
  FIXCHAR(hostname,cl0,_cltmp0);
*ierr = PetscOpenSocket(_cltmp0,*portnum,t);
  FREECHAR(hostname,_cltmp0);
}
PETSC_EXTERN void  petscviewersocketopen_(MPI_Fint * comm, char machine[],int *port,PetscViewer *lab, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
PetscBool lab_null = !*(void**) lab ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(lab);
/* insert Fortran-to-C conversion for machine */
  FIXCHAR(machine,cl0,_cltmp0);
*ierr = PetscViewerSocketOpen(
	MPI_Comm_f2c(*(comm)),_cltmp0,*port,lab);
  FREECHAR(machine,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! lab_null && !*(void**) lab) * (void **) lab = (void *)-2;
}
PETSC_EXTERN void  petscviewersocketsetconnection_(PetscViewer v, char machine[],int *port, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(v);
/* insert Fortran-to-C conversion for machine */
  FIXCHAR(machine,cl0,_cltmp0);
*ierr = PetscViewerSocketSetConnection(PetscPatchDefaultViewers((PetscViewer*)v),_cltmp0,*port);
  FREECHAR(machine,_cltmp0);
}
#if defined(__cplusplus)
}
#endif
