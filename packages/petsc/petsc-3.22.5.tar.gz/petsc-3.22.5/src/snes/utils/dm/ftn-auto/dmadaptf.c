#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* dmadapt.c */
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

#include "petscdmadaptor.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmadaptorcreate_ DMADAPTORCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmadaptorcreate_ dmadaptorcreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmadaptordestroy_ DMADAPTORDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmadaptordestroy_ dmadaptordestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmadaptorsettype_ DMADAPTORSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmadaptorsettype_ dmadaptorsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmadaptorgettype_ DMADAPTORGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmadaptorgettype_ dmadaptorgettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmadaptormonitorcancel_ DMADAPTORMONITORCANCEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmadaptormonitorcancel_ dmadaptormonitorcancel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmadaptorsetoptionsprefix_ DMADAPTORSETOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmadaptorsetoptionsprefix_ dmadaptorsetoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmadaptorsetfromoptions_ DMADAPTORSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmadaptorsetfromoptions_ dmadaptorsetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmadaptorview_ DMADAPTORVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmadaptorview_ dmadaptorview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmadaptorgetsolver_ DMADAPTORGETSOLVER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmadaptorgetsolver_ dmadaptorgetsolver
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmadaptorsetsolver_ DMADAPTORSETSOLVER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmadaptorsetsolver_ dmadaptorsetsolver
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmadaptorgetsequencelength_ DMADAPTORGETSEQUENCELENGTH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmadaptorgetsequencelength_ dmadaptorgetsequencelength
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmadaptorsetsequencelength_ DMADAPTORSETSEQUENCELENGTH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmadaptorsetsequencelength_ dmadaptorsetsequencelength
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmadaptorsetup_ DMADAPTORSETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmadaptorsetup_ dmadaptorsetup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmadaptormonitor_ DMADAPTORMONITOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmadaptormonitor_ dmadaptormonitor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmadaptoradapt_ DMADAPTORADAPT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmadaptoradapt_ dmadaptoradapt
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmadaptorcreate_(MPI_Fint * comm,DMAdaptor *adaptor, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(adaptor);
 PetscBool adaptor_null = !*(void**) adaptor ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(adaptor);
*ierr = DMAdaptorCreate(
	MPI_Comm_f2c(*(comm)),adaptor);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! adaptor_null && !*(void**) adaptor) * (void **) adaptor = (void *)-2;
}
PETSC_EXTERN void  dmadaptordestroy_(DMAdaptor *adaptor, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(adaptor);
 PetscBool adaptor_null = !*(void**) adaptor ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(adaptor);
*ierr = DMAdaptorDestroy(adaptor);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! adaptor_null && !*(void**) adaptor) * (void **) adaptor = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(adaptor);
 }
PETSC_EXTERN void  dmadaptorsettype_(DMAdaptor adaptor,char *method, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(adaptor);
/* insert Fortran-to-C conversion for method */
  FIXCHAR(method,cl0,_cltmp0);
*ierr = DMAdaptorSetType(
	(DMAdaptor)PetscToPointer((adaptor) ),_cltmp0);
  FREECHAR(method,_cltmp0);
}
PETSC_EXTERN void  dmadaptorgettype_(DMAdaptor adaptor,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(adaptor);
*ierr = DMAdaptorGetType(
	(DMAdaptor)PetscToPointer((adaptor) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for type */
*ierr = PetscStrncpy(type, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, type, cl0);
}
PETSC_EXTERN void  dmadaptormonitorcancel_(DMAdaptor adaptor, int *ierr)
{
CHKFORTRANNULLOBJECT(adaptor);
*ierr = DMAdaptorMonitorCancel(
	(DMAdaptor)PetscToPointer((adaptor) ));
}
PETSC_EXTERN void  dmadaptorsetoptionsprefix_(DMAdaptor adaptor, char prefix[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(adaptor);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = DMAdaptorSetOptionsPrefix(
	(DMAdaptor)PetscToPointer((adaptor) ),_cltmp0);
  FREECHAR(prefix,_cltmp0);
}
PETSC_EXTERN void  dmadaptorsetfromoptions_(DMAdaptor adaptor, int *ierr)
{
CHKFORTRANNULLOBJECT(adaptor);
*ierr = DMAdaptorSetFromOptions(
	(DMAdaptor)PetscToPointer((adaptor) ));
}
PETSC_EXTERN void  dmadaptorview_(DMAdaptor adaptor,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(adaptor);
CHKFORTRANNULLOBJECT(viewer);
*ierr = DMAdaptorView(
	(DMAdaptor)PetscToPointer((adaptor) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  dmadaptorgetsolver_(DMAdaptor adaptor,SNES *snes, int *ierr)
{
CHKFORTRANNULLOBJECT(adaptor);
PetscBool snes_null = !*(void**) snes ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(snes);
*ierr = DMAdaptorGetSolver(
	(DMAdaptor)PetscToPointer((adaptor) ),snes);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! snes_null && !*(void**) snes) * (void **) snes = (void *)-2;
}
PETSC_EXTERN void  dmadaptorsetsolver_(DMAdaptor adaptor,SNES snes, int *ierr)
{
CHKFORTRANNULLOBJECT(adaptor);
CHKFORTRANNULLOBJECT(snes);
*ierr = DMAdaptorSetSolver(
	(DMAdaptor)PetscToPointer((adaptor) ),
	(SNES)PetscToPointer((snes) ));
}
PETSC_EXTERN void  dmadaptorgetsequencelength_(DMAdaptor adaptor,PetscInt *num, int *ierr)
{
CHKFORTRANNULLOBJECT(adaptor);
CHKFORTRANNULLINTEGER(num);
*ierr = DMAdaptorGetSequenceLength(
	(DMAdaptor)PetscToPointer((adaptor) ),num);
}
PETSC_EXTERN void  dmadaptorsetsequencelength_(DMAdaptor adaptor,PetscInt *num, int *ierr)
{
CHKFORTRANNULLOBJECT(adaptor);
*ierr = DMAdaptorSetSequenceLength(
	(DMAdaptor)PetscToPointer((adaptor) ),*num);
}
PETSC_EXTERN void  dmadaptorsetup_(DMAdaptor adaptor, int *ierr)
{
CHKFORTRANNULLOBJECT(adaptor);
*ierr = DMAdaptorSetUp(
	(DMAdaptor)PetscToPointer((adaptor) ));
}
PETSC_EXTERN void  dmadaptormonitor_(DMAdaptor adaptor,PetscInt *it,DM odm,DM adm,PetscInt *Nf,PetscReal enorms[],Vec error, int *ierr)
{
CHKFORTRANNULLOBJECT(adaptor);
CHKFORTRANNULLOBJECT(odm);
CHKFORTRANNULLOBJECT(adm);
CHKFORTRANNULLREAL(enorms);
CHKFORTRANNULLOBJECT(error);
*ierr = DMAdaptorMonitor(
	(DMAdaptor)PetscToPointer((adaptor) ),*it,
	(DM)PetscToPointer((odm) ),
	(DM)PetscToPointer((adm) ),*Nf,enorms,
	(Vec)PetscToPointer((error) ));
}
PETSC_EXTERN void  dmadaptoradapt_(DMAdaptor adaptor,Vec x,DMAdaptationStrategy *strategy,DM *adm,Vec *ax, int *ierr)
{
CHKFORTRANNULLOBJECT(adaptor);
CHKFORTRANNULLOBJECT(x);
PetscBool adm_null = !*(void**) adm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(adm);
PetscBool ax_null = !*(void**) ax ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ax);
*ierr = DMAdaptorAdapt(
	(DMAdaptor)PetscToPointer((adaptor) ),
	(Vec)PetscToPointer((x) ),*strategy,adm,ax);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! adm_null && !*(void**) adm) * (void **) adm = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ax_null && !*(void**) ax) * (void **) ax = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
